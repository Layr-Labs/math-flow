from __future__ import annotations

import copy
import re
from collections.abc import Callable, Mapping, Sequence

from .errors import MathFlowError
from .repository import sha256_json
from .research_builder_v7 import validate_research_program_state_v3
from .research_builder_v9 import apply_research_builder_v9_transition


ENTITY_KINDS = {"program", "intermediateResult"}
CATALOG_FIELDS = {
    "schemaVersion",
    "problemId",
    "baseStateDigest",
    "rootProgramId",
    "programCards",
    "resultCards",
    "programDirectory",
    "catalogDigest",
}
PROGRAM_CARD_FIELDS = {
    "entityKind",
    "entityId",
    "parentId",
    "title",
    "objective",
    "currentStateSummary",
    "localResidualSummary",
    "status",
    "cardDigest",
}
RESULT_CARD_FIELDS = {
    "entityKind",
    "entityId",
    "primaryProgramId",
    "relatedProgramIds",
    "title",
    "statement",
    "scopeQualifications",
    "dependencyResultIds",
    "status",
    "cardDigest",
}
DIRECTORY_FIELDS = {
    "programId",
    "childProgramIds",
    "linkedResultIds",
    "descendantProgramCount",
    "descendantLinkedResultCount",
    "subtreeDigest",
    "directoryDigest",
}
CAPSULE_FIELDS = {
    "schemaVersion",
    "problemId",
    "baseStateDigest",
    "catalogDigest",
    "program",
    "childProgramOffset",
    "childProgramLimit",
    "childProgramCount",
    "nextChildProgramOffset",
    "childPrograms",
    "linkedResultOffset",
    "linkedResultLimit",
    "linkedResultCount",
    "nextLinkedResultOffset",
    "linkedResults",
    "descendantProgramCount",
    "descendantLinkedResultCount",
    "subtreeDigest",
    "capsuleDigest",
}
ROUTE_CONTEXT_FIELDS = {
    "schemaVersion",
    "problemId",
    "baseStateDigest",
    "acceptedClaimsDigest",
    "catalogDigest",
    "rootProgramId",
    "dependencyTransactionIds",
    "dependencyResultIds",
    "maxDependencyResults",
    "dependencyResults",
    "rootCapsule",
    "contextDigest",
}
RAW_ROUTE_PLAN_FIELDS = {
    "schemaVersion",
    "baseStateDigest",
    "routeContextDigest",
    "inspectProgramIds",
    "inspectResultIds",
    "searchQueries",
    "writeProgramIds",
    "writeResultIds",
    "createProgramIds",
    "createResultIds",
}
ROUTE_PLAN_FIELDS = RAW_ROUTE_PLAN_FIELDS | {"routePlanDigest"}
SEARCH_QUERY_FIELDS = {"query", "entityKinds", "limit"}
PROGRAM_VIEW_FIELDS = {
    "id",
    "parentId",
    "title",
    "objective",
    "currentStateSummary",
    "localResidualSummary",
    "status",
    "lineage",
    "recordDigest",
    "linkedResultCount",
    "linkedResultIdsDigest",
    "sourceTransactionCount",
    "sourceTransactionIdsDigest",
}
RESULT_VIEW_FIELDS = {
    "id",
    "primaryProgramId",
    "relatedProgramIds",
    "title",
    "statement",
    "scopeQualifications",
    "supportCounts",
    "supportDigest",
    "dependencyResultIds",
    "claimRefCount",
    "claimRefsDigest",
    "sourceTransactionCount",
    "sourceTransactionIdsDigest",
    "judgmentCount",
    "judgmentIdsDigest",
    "status",
    "supersededByResultIds",
    "recordDigest",
}
SUPPORT_COUNT_FIELDS = {
    "proofs",
    "methods",
    "computations",
    "tools",
    "artifactRefs",
    "attestationRefs",
}
READ_SET_FIELDS = {
    "programIds",
    "resultIds",
    "ancestorProgramIds",
    "dependencyResultIds",
    "searchProgramIds",
    "searchResultIds",
}
WRITE_SCOPE_FIELDS = {
    "existingProgramIds",
    "existingResultIds",
    "createProgramIds",
    "createResultIds",
}
LIMIT_FIELDS = {
    "maxPrograms",
    "maxResults",
    "capsuleChildLimit",
    "capsuleResultLimit",
}
HIDDEN_COMMITMENT_FIELDS = {
    "stateDigest",
    "programCount",
    "resultCount",
    "contributionCount",
    "programIdsDigest",
    "resultIdsDigest",
}
AUTHORING_PACKET_FIELDS = {
    "schemaVersion",
    "problemId",
    "baseStateDigest",
    "acceptedClaimsDigest",
    "catalogDigest",
    "routeContext",
    "routePlan",
    "limits",
    "readSet",
    "writeScope",
    "programs",
    "intermediateResults",
    "programCapsules",
    "searchResults",
    "hiddenStateCommitment",
    "authoringPacketDigest",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _digest(value: Mapping[str, object], field: str) -> str:
    core = {
        key: copy.deepcopy(item) for key, item in value.items() if key != field
    }
    return f"sha256:{sha256_json(core)}"


def _list_digest(values: Sequence[object]) -> str:
    return f"sha256:{sha256_json(list(values))}"


def _unique_strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise MathFlowError(f"{label} must be an array of strings")
    if len(value) != len(set(value)) or any(not item for item in value):
        raise MathFlowError(f"{label} must contain unique non-empty strings")
    return sorted(value)


def _positive_limit(value: object, label: str, *, maximum: int = 256) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > maximum
    ):
        raise MathFlowError(f"{label} must be between 1 and {maximum}")
    return value


def _card_digest(value: Mapping[str, object]) -> str:
    return _digest(value, "cardDigest")


def _program_card(program: Mapping[str, object]) -> dict[str, object]:
    core: dict[str, object] = {
        "entityKind": "program",
        "entityId": program["id"],
        "parentId": program["parentId"],
        "title": program["title"],
        "objective": program["objective"],
        "currentStateSummary": program["currentStateSummary"],
        "localResidualSummary": program["localResidualSummary"],
        "status": program["status"],
    }
    return {**core, "cardDigest": _card_digest(core)}


def _result_card(result: Mapping[str, object]) -> dict[str, object]:
    core: dict[str, object] = {
        "entityKind": "intermediateResult",
        "entityId": result["id"],
        "primaryProgramId": result["primaryProgramId"],
        "relatedProgramIds": copy.deepcopy(result["relatedProgramIds"]),
        "title": result["title"],
        "statement": result["statement"],
        "scopeQualifications": copy.deepcopy(result["scopeQualifications"]),
        "dependencyResultIds": copy.deepcopy(result["dependencyResultIds"]),
        "status": result["status"],
    }
    return {**core, "cardDigest": _card_digest(core)}


def build_research_builder_v10_catalog(
    base_state: Mapping[str, object],
) -> dict[str, object]:
    """Derive the trusted compact directory used for routing.

    Cards intentionally omit support and cumulative claim/source/judgment
    provenance. The catalog is trusted internal state; callers expose only
    bounded capsule pages and search hits to the organizer.
    """

    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    programs = state["programs"]
    results = state["intermediateResults"]
    assert isinstance(programs, dict)
    assert isinstance(results, dict)
    program_cards = {
        str(program_id): _program_card(program)
        for program_id, program in sorted(programs.items())
        if isinstance(program, dict)
    }
    result_cards = {
        str(result_id): _result_card(result)
        for result_id, result in sorted(results.items())
        if isinstance(result, dict)
    }
    children: dict[str, list[str]] = {str(program_id): [] for program_id in programs}
    for program_id, program in programs.items():
        if isinstance(program, dict) and isinstance(program.get("parentId"), str):
            children[str(program["parentId"])].append(str(program_id))
    for values in children.values():
        values.sort()

    memo: dict[str, tuple[int, int, str]] = {}

    def subtree(program_id: str) -> tuple[int, int, str]:
        if program_id in memo:
            return memo[program_id]
        child_entries = []
        descendant_programs = 0
        descendant_results = 0
        for child_id in children[program_id]:
            child_programs, child_results, child_digest = subtree(child_id)
            descendant_programs += 1 + child_programs
            descendant_results += child_results
            child_entries.append({"programId": child_id, "subtreeDigest": child_digest})
        program = programs[program_id]
        assert isinstance(program, dict)
        linked = sorted(str(item) for item in program["intermediateResultIds"])
        descendant_results += len(linked)
        digest = f"sha256:{sha256_json({'programDigest': program['digest'], 'linkedResultDigests': [results[result_id]['digest'] for result_id in linked], 'children': child_entries})}"
        memo[program_id] = (descendant_programs, descendant_results, digest)
        return memo[program_id]

    directory: dict[str, dict[str, object]] = {}
    for program_id in sorted(programs):
        descendant_programs, descendant_results, subtree_digest = subtree(str(program_id))
        program = programs[program_id]
        assert isinstance(program, dict)
        entry: dict[str, object] = {
            "programId": str(program_id),
            "childProgramIds": children[str(program_id)],
            "linkedResultIds": sorted(str(item) for item in program["intermediateResultIds"]),
            "descendantProgramCount": descendant_programs,
            "descendantLinkedResultCount": descendant_results,
            "subtreeDigest": subtree_digest,
        }
        directory[str(program_id)] = {
            **entry,
            "directoryDigest": _digest(entry, "directoryDigest"),
        }
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": state["problemId"],
        "baseStateDigest": state["stateDigest"],
        "rootProgramId": state["rootProgramId"],
        "programCards": program_cards,
        "resultCards": result_cards,
        "programDirectory": directory,
    }
    return {**core, "catalogDigest": _digest(core, "catalogDigest")}


def validate_research_builder_v10_catalog(
    value: object, *, base_state: Mapping[str, object] | None = None
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != CATALOG_FIELDS:
        raise MathFlowError("research builder v10 catalog has an invalid envelope")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("research builder v10 catalog has an unsupported version")
    if value.get("catalogDigest") != _digest(value, "catalogDigest"):
        raise MathFlowError("research builder v10 catalog digest mismatch")
    programs = value.get("programCards")
    results = value.get("resultCards")
    directory = value.get("programDirectory")
    root_id = value.get("rootProgramId")
    if not isinstance(programs, dict) or not isinstance(results, dict) or not isinstance(directory, dict):
        raise MathFlowError("research builder v10 catalog collections are invalid")
    if not isinstance(root_id, str) or root_id not in programs or set(programs) != set(directory):
        raise MathFlowError("research builder v10 catalog program directory is incomplete")
    for program_id, card in programs.items():
        if (
            not isinstance(program_id, str)
            or not isinstance(card, dict)
            or set(card) != PROGRAM_CARD_FIELDS
            or card.get("entityKind") != "program"
            or card.get("entityId") != program_id
            or card.get("cardDigest") != _card_digest(card)
        ):
            raise MathFlowError("research builder v10 program card is invalid")
    for result_id, card in results.items():
        if (
            not isinstance(result_id, str)
            or not isinstance(card, dict)
            or set(card) != RESULT_CARD_FIELDS
            or card.get("entityKind") != "intermediateResult"
            or card.get("entityId") != result_id
            or card.get("cardDigest") != _card_digest(card)
        ):
            raise MathFlowError("research builder v10 result card is invalid")
    for program_id, entry in directory.items():
        if (
            not isinstance(entry, dict)
            or set(entry) != DIRECTORY_FIELDS
            or entry.get("programId") != program_id
            or entry.get("directoryDigest") != _digest(entry, "directoryDigest")
        ):
            raise MathFlowError("research builder v10 directory entry is invalid")
        child_ids = _unique_strings(entry.get("childProgramIds"), "directory children")
        result_ids = _unique_strings(entry.get("linkedResultIds"), "directory results")
        if not set(child_ids) <= set(programs) or not set(result_ids) <= set(results):
            raise MathFlowError("research builder v10 directory references an unknown entity")
    if base_state is not None and value != build_research_builder_v10_catalog(base_state):
        raise MathFlowError("research builder v10 catalog is not reducer-derived")
    return value


def build_research_builder_v10_program_capsule(
    catalog: Mapping[str, object],
    program_id: str,
    *,
    child_offset: int = 0,
    result_offset: int = 0,
    max_children: int = 12,
    max_results: int = 12,
) -> dict[str, object]:
    catalog_value = validate_research_builder_v10_catalog(copy.deepcopy(dict(catalog)))
    if not isinstance(child_offset, int) or isinstance(child_offset, bool) or child_offset < 0:
        raise MathFlowError("research builder v10 capsule child offset is invalid")
    if not isinstance(result_offset, int) or isinstance(result_offset, bool) or result_offset < 0:
        raise MathFlowError("research builder v10 capsule result offset is invalid")
    child_limit = _positive_limit(max_children, "capsule child limit")
    result_limit = _positive_limit(max_results, "capsule result limit")
    cards = catalog_value["programCards"]
    results = catalog_value["resultCards"]
    directory = catalog_value["programDirectory"]
    assert isinstance(cards, dict) and isinstance(results, dict) and isinstance(directory, dict)
    entry = directory.get(program_id)
    if not isinstance(entry, dict):
        raise MathFlowError(f"research builder v10 capsule program is absent: {program_id}")
    child_ids = list(entry["childProgramIds"])
    result_ids = list(entry["linkedResultIds"])
    child_page = child_ids[child_offset : child_offset + child_limit]
    result_page = result_ids[result_offset : result_offset + result_limit]
    next_child = child_offset + len(child_page)
    next_result = result_offset + len(result_page)
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": catalog_value["problemId"],
        "baseStateDigest": catalog_value["baseStateDigest"],
        "catalogDigest": catalog_value["catalogDigest"],
        "program": copy.deepcopy(cards[program_id]),
        "childProgramOffset": child_offset,
        "childProgramLimit": child_limit,
        "childProgramCount": len(child_ids),
        "nextChildProgramOffset": next_child if next_child < len(child_ids) else None,
        "childPrograms": [copy.deepcopy(cards[item]) for item in child_page],
        "linkedResultOffset": result_offset,
        "linkedResultLimit": result_limit,
        "linkedResultCount": len(result_ids),
        "nextLinkedResultOffset": next_result if next_result < len(result_ids) else None,
        "linkedResults": [copy.deepcopy(results[item]) for item in result_page],
        "descendantProgramCount": entry["descendantProgramCount"],
        "descendantLinkedResultCount": entry["descendantLinkedResultCount"],
        "subtreeDigest": entry["subtreeDigest"],
    }
    return {**core, "capsuleDigest": _digest(core, "capsuleDigest")}


def _search_text(card: Mapping[str, object]) -> str:
    fields = (
        "entityId",
        "title",
        "objective",
        "currentStateSummary",
        "localResidualSummary",
        "statement",
    )
    values = [str(card[field]) for field in fields if isinstance(card.get(field), str)]
    qualifications = card.get("scopeQualifications")
    if isinstance(qualifications, list):
        values.extend(str(item) for item in qualifications if isinstance(item, str))
    return " ".join(values).lower()


def search_research_builder_v10_catalog(
    catalog: Mapping[str, object],
    query: str,
    *,
    entity_kinds: Sequence[str] = ("program", "intermediateResult"),
    limit: int = 8,
) -> list[dict[str, object]]:
    catalog_value = validate_research_builder_v10_catalog(copy.deepcopy(dict(catalog)))
    if not isinstance(query, str) or not query.strip():
        raise MathFlowError("research builder v10 search query must be non-empty")
    kinds = sorted(set(entity_kinds))
    if not kinds or any(kind not in ENTITY_KINDS for kind in kinds):
        raise MathFlowError("research builder v10 search entity kinds are invalid")
    result_limit = _positive_limit(limit, "research builder v10 search limit", maximum=32)
    query_text = query.strip().lower()
    query_terms = set(TOKEN_RE.findall(query_text))
    if not query_terms:
        raise MathFlowError("research builder v10 search query has no searchable terms")
    candidates: list[dict[str, object]] = []
    collections = []
    if "program" in kinds:
        collections.append(catalog_value["programCards"])
    if "intermediateResult" in kinds:
        collections.append(catalog_value["resultCards"])
    for collection in collections:
        assert isinstance(collection, dict)
        for card in collection.values():
            assert isinstance(card, dict)
            text = _search_text(card)
            matched = sorted(query_terms & set(TOKEN_RE.findall(text)))
            if not matched:
                continue
            score = (
                (1_000_000 if query_text in text else 0)
                + len(matched) * 1_000
                + len(matched) * 1_000 // len(query_terms)
            )
            candidates.append(
                {
                    "entityKind": card["entityKind"],
                    "entityId": card["entityId"],
                    "score": score,
                    "matchedTerms": matched,
                    "card": copy.deepcopy(card),
                }
            )
    candidates.sort(
        key=lambda item: (-int(item["score"]), str(item["entityKind"]), str(item["entityId"]))
    )
    return candidates[:result_limit]


def _dependency_transaction_ids(accepted_claims: object) -> list[str]:
    if not isinstance(accepted_claims, list) or not accepted_claims:
        raise MathFlowError("research builder v10 needs accepted claims")
    dependencies: set[str] = set()
    for claim in accepted_claims:
        raw = claim.get("dependencyTransactionIds") if isinstance(claim, dict) else None
        if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
            raise MathFlowError("research builder v10 claim dependencies are invalid")
        dependencies.update(raw)
    return sorted(dependencies)


def _result_dependency_closure(
    state: Mapping[str, object], result_ids: Sequence[str]
) -> set[str]:
    results = state.get("intermediateResults")
    if not isinstance(results, dict):
        raise MathFlowError("research builder v10 state has no intermediate results")
    loaded: set[str] = set()
    pending = list(result_ids)
    while pending:
        result_id = pending.pop()
        if result_id in loaded:
            continue
        result = results.get(result_id)
        if not isinstance(result, dict):
            raise MathFlowError(f"research builder v10 result is absent: {result_id}")
        loaded.add(result_id)
        dependencies = result.get("dependencyResultIds")
        if not isinstance(dependencies, list):
            raise MathFlowError("research builder v10 result dependencies are invalid")
        pending.extend(str(item) for item in dependencies)
    return loaded


def _result_read_closure(
    state: Mapping[str, object], result_ids: Sequence[str]
) -> set[str]:
    """Load logical prerequisites and live successors needed to interpret a result."""

    results = state.get("intermediateResults")
    if not isinstance(results, dict):
        raise MathFlowError("research builder v10 state has no intermediate results")
    loaded: set[str] = set()
    pending = list(result_ids)
    while pending:
        result_id = pending.pop()
        if result_id in loaded:
            continue
        result = results.get(result_id)
        if not isinstance(result, dict):
            raise MathFlowError(f"research builder v10 result is absent: {result_id}")
        loaded.add(result_id)
        for field in ("dependencyResultIds", "supersededByResultIds"):
            references = result.get(field)
            if not isinstance(references, list):
                raise MathFlowError("research builder v10 result references are invalid")
            pending.extend(str(item) for item in references)
    return loaded


def _declared_dependency_result_ids(
    state: Mapping[str, object], accepted_claims: object
) -> tuple[list[str], list[str]]:
    transactions = _dependency_transaction_ids(accepted_claims)
    contributions = state.get("contributions")
    if not isinstance(contributions, dict):
        raise MathFlowError("research builder v10 state has no contributions")
    seeds: list[str] = []
    for transaction_id in transactions:
        contribution = contributions.get(transaction_id)
        if not isinstance(contribution, dict):
            raise MathFlowError(
                f"research builder v10 dependency is absent from predecessor: {transaction_id}"
            )
        result_ids = contribution.get("intermediateResultIds")
        if not isinstance(result_ids, list):
            raise MathFlowError("research builder v10 contribution mapping is invalid")
        seeds.extend(str(item) for item in result_ids)
    return transactions, sorted(_result_dependency_closure(state, seeds))


def build_research_builder_v10_route_context(
    base_state: Mapping[str, object],
    accepted_claims: object,
    *,
    max_root_children: int = 12,
    max_root_results: int = 12,
    max_dependency_results: int = 64,
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    catalog = build_research_builder_v10_catalog(state)
    transactions, result_ids = _declared_dependency_result_ids(state, accepted_claims)
    dependency_limit = _positive_limit(
        max_dependency_results,
        "route dependency result limit",
        maximum=1024,
    )
    if len(result_ids) > dependency_limit:
        raise MathFlowError(
            "research builder v10 route dependency closure exceeds budget: "
            f"{len(result_ids)} > {dependency_limit}"
        )
    result_cards = catalog["resultCards"]
    assert isinstance(result_cards, dict)
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": state["problemId"],
        "baseStateDigest": state["stateDigest"],
        "acceptedClaimsDigest": f"sha256:{sha256_json(accepted_claims)}",
        "catalogDigest": catalog["catalogDigest"],
        "rootProgramId": state["rootProgramId"],
        "dependencyTransactionIds": transactions,
        "dependencyResultIds": result_ids,
        "maxDependencyResults": dependency_limit,
        "dependencyResults": [copy.deepcopy(result_cards[item]) for item in result_ids],
        "rootCapsule": build_research_builder_v10_program_capsule(
            catalog,
            str(state["rootProgramId"]),
            max_children=max_root_children,
            max_results=max_root_results,
        ),
    }
    return {**core, "contextDigest": _digest(core, "contextDigest")}


def validate_research_builder_v10_route_context(
    value: object,
    *,
    base_state: Mapping[str, object] | None = None,
    accepted_claims: object | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != ROUTE_CONTEXT_FIELDS:
        raise MathFlowError("research builder v10 route context has an invalid envelope")
    if value.get("schemaVersion") != 1 or value.get("contextDigest") != _digest(value, "contextDigest"):
        raise MathFlowError("research builder v10 route context digest/version is invalid")
    capsule = value.get("rootCapsule")
    if not isinstance(capsule, dict) or set(capsule) != CAPSULE_FIELDS:
        raise MathFlowError("research builder v10 root capsule is invalid")
    if capsule.get("capsuleDigest") != _digest(capsule, "capsuleDigest"):
        raise MathFlowError("research builder v10 root capsule digest mismatch")
    dependency_ids = _unique_strings(value.get("dependencyResultIds"), "route dependency results")
    dependency_cards = value.get("dependencyResults")
    if (
        not isinstance(dependency_cards, list)
        or [item.get("entityId") if isinstance(item, dict) else None for item in dependency_cards]
        != dependency_ids
    ):
        raise MathFlowError("research builder v10 route dependency cards are invalid")
    if base_state is not None:
        if accepted_claims is None:
            raise MathFlowError("research builder v10 route validation needs claims")
        child_limit = capsule.get("childProgramLimit")
        result_limit = capsule.get("linkedResultLimit")
        dependency_limit = value.get("maxDependencyResults")
        expected = build_research_builder_v10_route_context(
            base_state,
            accepted_claims,
            max_root_children=int(child_limit),
            max_root_results=int(result_limit),
            max_dependency_results=int(dependency_limit),
        )
        if value != expected:
            raise MathFlowError("research builder v10 route context is not reducer-derived")
    return value


def _raw_route_plan(route_plan: Mapping[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(item)
        for key, item in route_plan.items()
        if key != "routePlanDigest"
    }


def bind_research_builder_v10_route_plan(
    route_context: Mapping[str, object],
    catalog: Mapping[str, object],
    route_plan: object,
    *,
    max_programs: int = 64,
    max_results: int = 64,
) -> dict[str, object]:
    context = validate_research_builder_v10_route_context(copy.deepcopy(dict(route_context)))
    catalog_value = validate_research_builder_v10_catalog(copy.deepcopy(dict(catalog)))
    program_limit = _positive_limit(
        max_programs, "route program limit", maximum=1024
    )
    result_limit = _positive_limit(max_results, "route result limit", maximum=1024)
    if not isinstance(route_plan, dict):
        raise MathFlowError("research builder v10 route plan must be an object")
    raw = _raw_route_plan(route_plan)
    if set(raw) != RAW_ROUTE_PLAN_FIELDS or raw.get("schemaVersion") != 1:
        raise MathFlowError("research builder v10 route plan has invalid fields")
    if raw.get("baseStateDigest") != context["baseStateDigest"] or raw.get("routeContextDigest") != context["contextDigest"]:
        raise MathFlowError("research builder v10 route plan has a stale binding")
    normalized: dict[str, object] = {
        "schemaVersion": 1,
        "baseStateDigest": raw["baseStateDigest"],
        "routeContextDigest": raw["routeContextDigest"],
    }
    program_cards = catalog_value["programCards"]
    result_cards = catalog_value["resultCards"]
    assert isinstance(program_cards, dict) and isinstance(result_cards, dict)
    for field, collection in (
        ("inspectProgramIds", program_cards),
        ("inspectResultIds", result_cards),
        ("writeProgramIds", program_cards),
        ("writeResultIds", result_cards),
    ):
        ids = _unique_strings(raw.get(field), f"route {field}")
        if not set(ids) <= set(collection):
            raise MathFlowError(f"research builder v10 route {field} names an unknown entity")
        normalized[field] = ids
    for field, collection in (
        ("createProgramIds", program_cards),
        ("createResultIds", result_cards),
    ):
        ids = _unique_strings(raw.get(field), f"route {field}")
        if set(ids) & set(collection) or (field == "createProgramIds" and "root" in ids):
            raise MathFlowError(f"research builder v10 route {field} is not new")
        normalized[field] = ids
    requested_program_ids = (
        set(normalized["inspectProgramIds"])
        | set(normalized["writeProgramIds"])
        | set(normalized["createProgramIds"])
    )
    requested_result_ids = (
        set(normalized["inspectResultIds"])
        | set(normalized["writeResultIds"])
        | set(normalized["createResultIds"])
    )
    if len(requested_program_ids) > program_limit:
        raise MathFlowError(
            "research builder v10 route program ID scope exceeds budget: "
            f"{len(requested_program_ids)} > {program_limit}"
        )
    if len(requested_result_ids) > result_limit:
        raise MathFlowError(
            "research builder v10 route result ID scope exceeds budget: "
            f"{len(requested_result_ids)} > {result_limit}"
        )
    raw_queries = raw.get("searchQueries")
    if not isinstance(raw_queries, list) or len(raw_queries) > 8:
        raise MathFlowError("research builder v10 route has too many search queries")
    queries: list[dict[str, object]] = []
    seen_queries: set[tuple[str, tuple[str, ...], int]] = set()
    for raw_query in raw_queries:
        if not isinstance(raw_query, dict) or set(raw_query) != SEARCH_QUERY_FIELDS:
            raise MathFlowError("research builder v10 route search query is invalid")
        query = raw_query.get("query")
        kinds = _unique_strings(raw_query.get("entityKinds"), "route search entity kinds")
        limit = _positive_limit(raw_query.get("limit"), "route search limit", maximum=16)
        if not isinstance(query, str) or not query.strip() or not kinds or any(kind not in ENTITY_KINDS for kind in kinds):
            raise MathFlowError("research builder v10 route search query is invalid")
        entry = {"query": query.strip(), "entityKinds": kinds, "limit": limit}
        key = (str(entry["query"]), tuple(kinds), limit)
        if key in seen_queries:
            raise MathFlowError("research builder v10 route repeats a search query")
        seen_queries.add(key)
        queries.append(entry)
    normalized["searchQueries"] = queries
    canonical = {key: normalized[key] for key in RAW_ROUTE_PLAN_FIELDS}
    return {**canonical, "routePlanDigest": _digest(canonical, "routePlanDigest")}


def _ancestors(state: Mapping[str, object], program_ids: Sequence[str]) -> set[str]:
    programs = state.get("programs")
    if not isinstance(programs, dict):
        raise MathFlowError("research builder v10 state has no programs")
    ancestors: set[str] = set()
    for program_id in program_ids:
        cursor: str | None = program_id
        while cursor is not None:
            program = programs.get(cursor)
            if not isinstance(program, dict):
                raise MathFlowError(f"research builder v10 program is absent: {cursor}")
            ancestors.add(cursor)
            parent = program.get("parentId")
            cursor = str(parent) if isinstance(parent, str) else None
    return ancestors


def _program_view(program: Mapping[str, object]) -> dict[str, object]:
    linked = list(program["intermediateResultIds"])
    sources = list(program["sourceTransactionIds"])
    return {
        "id": program["id"],
        "parentId": program["parentId"],
        "title": program["title"],
        "objective": program["objective"],
        "currentStateSummary": program["currentStateSummary"],
        "localResidualSummary": program["localResidualSummary"],
        "status": program["status"],
        "lineage": copy.deepcopy(program["lineage"]),
        "recordDigest": program["digest"],
        "linkedResultCount": len(linked),
        "linkedResultIdsDigest": _list_digest(linked),
        "sourceTransactionCount": len(sources),
        "sourceTransactionIdsDigest": _list_digest(sources),
    }


def _result_view(result: Mapping[str, object]) -> dict[str, object]:
    support = result["support"]
    if not isinstance(support, dict):
        raise MathFlowError("research builder v10 result support is invalid")
    claim_refs = list(result["claimRefs"])
    source_ids = list(result["sourceTransactionIds"])
    judgment_ids = list(result["judgmentIds"])
    return {
        "id": result["id"],
        "primaryProgramId": result["primaryProgramId"],
        "relatedProgramIds": copy.deepcopy(result["relatedProgramIds"]),
        "title": result["title"],
        "statement": result["statement"],
        "scopeQualifications": copy.deepcopy(result["scopeQualifications"]),
        "supportCounts": {
            field: len(support[field])
            for field in sorted(SUPPORT_COUNT_FIELDS)
        },
        "supportDigest": f"sha256:{sha256_json(support)}",
        "dependencyResultIds": copy.deepcopy(result["dependencyResultIds"]),
        "claimRefCount": len(claim_refs),
        "claimRefsDigest": _list_digest(claim_refs),
        "sourceTransactionCount": len(source_ids),
        "sourceTransactionIdsDigest": _list_digest(source_ids),
        "judgmentCount": len(judgment_ids),
        "judgmentIdsDigest": _list_digest(judgment_ids),
        "status": result["status"],
        "supersededByResultIds": copy.deepcopy(result["supersededByResultIds"]),
        "recordDigest": result["digest"],
    }


def _hidden_commitment(state: Mapping[str, object]) -> dict[str, object]:
    programs = state["programs"]
    results = state["intermediateResults"]
    contributions = state["contributions"]
    assert isinstance(programs, dict) and isinstance(results, dict) and isinstance(contributions, dict)
    return {
        "stateDigest": state["stateDigest"],
        "programCount": len(programs),
        "resultCount": len(results),
        "contributionCount": len(contributions),
        "programIdsDigest": _list_digest(sorted(programs)),
        "resultIdsDigest": _list_digest(sorted(results)),
    }


def build_research_builder_v10_authoring_packet(
    base_state: Mapping[str, object],
    accepted_claims: object,
    route_plan: object,
    *,
    route_context: Mapping[str, object] | None = None,
    max_programs: int = 64,
    max_results: int = 64,
    capsule_child_limit: int = 8,
    capsule_result_limit: int = 8,
) -> dict[str, object]:
    state = validate_research_program_state_v3(copy.deepcopy(dict(base_state)))
    catalog = build_research_builder_v10_catalog(state)
    program_limit = _positive_limit(max_programs, "authoring program limit", maximum=1024)
    result_limit = _positive_limit(max_results, "authoring result limit", maximum=1024)
    context = (
        validate_research_builder_v10_route_context(
            copy.deepcopy(dict(route_context)),
            base_state=state,
            accepted_claims=accepted_claims,
        )
        if route_context is not None
        else build_research_builder_v10_route_context(state, accepted_claims)
    )
    plan = bind_research_builder_v10_route_plan(
        context,
        catalog,
        route_plan,
        max_programs=program_limit,
        max_results=result_limit,
    )
    child_limit = _positive_limit(capsule_child_limit, "authoring capsule child limit")
    linked_limit = _positive_limit(capsule_result_limit, "authoring capsule result limit")
    programs = state["programs"]
    results = state["intermediateResults"]
    assert isinstance(programs, dict) and isinstance(results, dict)

    search_results: list[dict[str, object]] = []
    search_program_ids: set[str] = set()
    search_result_ids: set[str] = set()
    for index, query in enumerate(plan["searchQueries"]):
        assert isinstance(query, dict)
        matches = search_research_builder_v10_catalog(
            catalog,
            str(query["query"]),
            entity_kinds=list(query["entityKinds"]),
            limit=int(query["limit"]),
        )
        compact_matches = []
        for match in matches:
            entity_id = str(match["entityId"])
            if match["entityKind"] == "program":
                search_program_ids.add(entity_id)
            else:
                search_result_ids.add(entity_id)
            compact_matches.append(
                {
                    "entityKind": match["entityKind"],
                    "entityId": entity_id,
                    "score": match["score"],
                    "matchedTerms": match["matchedTerms"],
                }
            )
        search_results.append(
            {"queryIndex": index, "query": copy.deepcopy(query), "matches": compact_matches}
        )

    dependency_ids = set(context["dependencyResultIds"])
    result_ids = (
        set(plan["inspectResultIds"])
        | set(plan["writeResultIds"])
        | search_result_ids
        | dependency_ids
    )
    result_ids = _result_read_closure(state, sorted(result_ids))
    program_ids = (
        set(plan["inspectProgramIds"])
        | set(plan["writeProgramIds"])
        | search_program_ids
    )
    for result_id in result_ids:
        result = results[result_id]
        assert isinstance(result, dict)
        program_ids.add(str(result["primaryProgramId"]))
        program_ids.update(str(item) for item in result["relatedProgramIds"])
    pending_program_ids = list(program_ids)
    while pending_program_ids:
        program_id = pending_program_ids.pop()
        program = programs.get(program_id)
        if not isinstance(program, dict):
            raise MathFlowError(f"research builder v10 program is absent: {program_id}")
        for item in program["lineage"]:
            lineage_id = str(item["programId"])
            if lineage_id not in program_ids:
                program_ids.add(lineage_id)
                pending_program_ids.append(lineage_id)
    prior_program_ids = set(program_ids)
    program_ids |= _ancestors(state, sorted(program_ids))
    ancestor_ids = program_ids - prior_program_ids
    if len(program_ids) > program_limit:
        raise MathFlowError(
            f"research builder v10 local program read-set exceeds budget: {len(program_ids)} > {program_limit}"
        )
    if len(result_ids) > result_limit:
        raise MathFlowError(
            f"research builder v10 local result read-set exceeds budget: {len(result_ids)} > {result_limit}"
        )
    created_program_ids = set(plan["createProgramIds"])
    created_result_ids = set(plan["createResultIds"])
    if len(program_ids) + len(created_program_ids) > program_limit:
        raise MathFlowError(
            "research builder v10 local program read/create scope exceeds budget: "
            f"{len(program_ids) + len(created_program_ids)} > {program_limit}"
        )
    if len(result_ids) + len(created_result_ids) > result_limit:
        raise MathFlowError(
            "research builder v10 local result read/create scope exceeds budget: "
            f"{len(result_ids) + len(created_result_ids)} > {result_limit}"
        )
    capsule_ids = (
        set(plan["inspectProgramIds"])
        | set(plan["writeProgramIds"])
        | search_program_ids
    )
    read_set = {
        "programIds": sorted(program_ids),
        "resultIds": sorted(result_ids),
        "ancestorProgramIds": sorted(ancestor_ids),
        "dependencyResultIds": sorted(dependency_ids),
        "searchProgramIds": sorted(search_program_ids),
        "searchResultIds": sorted(search_result_ids),
    }
    write_scope = {
        "existingProgramIds": list(plan["writeProgramIds"]),
        "existingResultIds": list(plan["writeResultIds"]),
        "createProgramIds": list(plan["createProgramIds"]),
        "createResultIds": list(plan["createResultIds"]),
    }
    if not set(write_scope["existingProgramIds"]) <= program_ids or not set(write_scope["existingResultIds"]) <= result_ids:
        raise MathFlowError("research builder v10 write scope is outside its read set")
    limits = {
        "maxPrograms": program_limit,
        "maxResults": result_limit,
        "capsuleChildLimit": child_limit,
        "capsuleResultLimit": linked_limit,
    }
    core: dict[str, object] = {
        "schemaVersion": 1,
        "problemId": state["problemId"],
        "baseStateDigest": state["stateDigest"],
        "acceptedClaimsDigest": f"sha256:{sha256_json(accepted_claims)}",
        "catalogDigest": catalog["catalogDigest"],
        "routeContext": copy.deepcopy(context),
        "routePlan": plan,
        "limits": limits,
        "readSet": read_set,
        "writeScope": write_scope,
        "programs": {
            program_id: _program_view(programs[program_id])
            for program_id in sorted(program_ids)
        },
        "intermediateResults": {
            result_id: _result_view(results[result_id])
            for result_id in sorted(result_ids)
        },
        "programCapsules": {
            program_id: build_research_builder_v10_program_capsule(
                catalog,
                program_id,
                max_children=child_limit,
                max_results=linked_limit,
            )
            for program_id in sorted(capsule_ids)
        },
        "searchResults": search_results,
        "hiddenStateCommitment": _hidden_commitment(state),
    }
    return {**core, "authoringPacketDigest": _digest(core, "authoringPacketDigest")}


def validate_research_builder_v10_authoring_packet(
    value: object,
    *,
    base_state: Mapping[str, object] | None = None,
    accepted_claims: object | None = None,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != AUTHORING_PACKET_FIELDS:
        raise MathFlowError("research builder v10 authoring packet has an invalid envelope")
    if value.get("schemaVersion") != 1 or value.get("authoringPacketDigest") != _digest(value, "authoringPacketDigest"):
        raise MathFlowError("research builder v10 authoring packet digest/version is invalid")
    for field, fields in (
        ("limits", LIMIT_FIELDS),
        ("readSet", READ_SET_FIELDS),
        ("writeScope", WRITE_SCOPE_FIELDS),
        ("hiddenStateCommitment", HIDDEN_COMMITMENT_FIELDS),
    ):
        record = value.get(field)
        if not isinstance(record, dict) or set(record) != fields:
            raise MathFlowError(f"research builder v10 authoring packet {field} is invalid")
    programs = value.get("programs")
    results = value.get("intermediateResults")
    if not isinstance(programs, dict) or not isinstance(results, dict):
        raise MathFlowError("research builder v10 authoring packet collections are invalid")
    if any(not isinstance(item, dict) or set(item) != PROGRAM_VIEW_FIELDS for item in programs.values()):
        raise MathFlowError("research builder v10 authoring program view is invalid")
    if any(not isinstance(item, dict) or set(item) != RESULT_VIEW_FIELDS for item in results.values()):
        raise MathFlowError("research builder v10 authoring result view is invalid")
    if base_state is not None:
        if accepted_claims is None:
            raise MathFlowError("research builder v10 authoring validation needs claims")
        limits = value["limits"]
        assert isinstance(limits, dict)
        route_plan = value["routePlan"]
        route_context = value["routeContext"]
        assert isinstance(route_plan, dict) and isinstance(route_context, dict)
        expected = build_research_builder_v10_authoring_packet(
            base_state,
            accepted_claims,
            _raw_route_plan(route_plan),
            route_context=route_context,
            max_programs=int(limits["maxPrograms"]),
            max_results=int(limits["maxResults"]),
            capsule_child_limit=int(limits["capsuleChildLimit"]),
            capsule_result_limit=int(limits["capsuleResultLimit"]),
        )
        if value != expected:
            raise MathFlowError("research builder v10 authoring packet is not reducer-derived")
    return value


def _operation_scope(
    base_state: Mapping[str, object],
    transition: Mapping[str, object],
    packet: Mapping[str, object],
) -> set[tuple[str, str]]:
    scope = packet["writeScope"]
    read_set = packet["readSet"]
    assert isinstance(scope, dict) and isinstance(read_set, dict)
    allowed_existing = {
        "program": set(scope["existingProgramIds"]),
        "intermediateResult": set(scope["existingResultIds"]),
    }
    allowed_created = {
        "program": set(scope["createProgramIds"]),
        "intermediateResult": set(scope["createResultIds"]),
    }
    readable = {
        "program": set(read_set["programIds"]) | allowed_created["program"],
        "intermediateResult": set(read_set["resultIds"]) | allowed_created["intermediateResult"],
    }
    base_collections = {
        "program": base_state["programs"],
        "intermediateResult": base_state["intermediateResults"],
    }
    limits = packet["limits"]
    assert isinstance(limits, dict)
    operation_limits = {
        "program": _positive_limit(
            limits["maxPrograms"], "transition program limit", maximum=1024
        ),
        "intermediateResult": _positive_limit(
            limits["maxResults"], "transition result limit", maximum=1024
        ),
    }
    maximum_operations = sum(operation_limits.values())
    operation_counts = {"program": 0, "intermediateResult": 0}
    operated: set[tuple[str, str]] = set()
    total_operations = 0
    for field in ("contentOperations", "topologyOperations"):
        operations = transition.get(field)
        if not isinstance(operations, list):
            raise MathFlowError("research builder v10 transition operations are invalid")
        if len(operations) > maximum_operations:
            raise MathFlowError(
                f"research builder v10 {field} exceeds operation budget: "
                f"{len(operations)} > {maximum_operations}"
            )
        total_operations += len(operations)
        if total_operations > maximum_operations:
            raise MathFlowError(
                "research builder v10 transition exceeds aggregate operation budget: "
                f"{total_operations} > {maximum_operations}"
            )
        for operation in operations:
            if not isinstance(operation, dict):
                raise MathFlowError("research builder v10 transition operation is invalid")
            kind = operation.get("entityKind")
            entity_id = operation.get("entityId")
            if kind not in ENTITY_KINDS or not isinstance(entity_id, str):
                raise MathFlowError("research builder v10 transition entity is invalid")
            operation_counts[str(kind)] += 1
            if operation_counts[str(kind)] > operation_limits[str(kind)]:
                raise MathFlowError(
                    f"research builder v10 transition {kind} operations exceed budget: "
                    f"{operation_counts[str(kind)]} > {operation_limits[str(kind)]}"
                )
            key = (str(kind), entity_id)
            if key in operated:
                raise MathFlowError("research builder v10 transition repeats an entity")
            collection = base_collections[str(kind)]
            assert isinstance(collection, dict)
            expected_scope = allowed_existing[str(kind)] if entity_id in collection else allowed_created[str(kind)]
            if entity_id not in expected_scope:
                raise MathFlowError(
                    f"research builder v10 transition writes outside scope: {kind} {entity_id}"
                )
            value = operation.get("value")
            if isinstance(value, dict):
                if kind == "program":
                    references = []
                    parent = value.get("parentId")
                    if isinstance(parent, str):
                        references.append(parent)
                    lineage = value.get("lineage")
                    if isinstance(lineage, list):
                        references.extend(
                            str(item["programId"])
                            for item in lineage
                            if isinstance(item, dict) and isinstance(item.get("programId"), str)
                        )
                    if not set(references) <= readable["program"]:
                        raise MathFlowError("research builder v10 program operation references unread state")
                else:
                    program_refs = []
                    primary = value.get("primaryProgramId")
                    if isinstance(primary, str):
                        program_refs.append(primary)
                    related = value.get("relatedProgramIds")
                    if isinstance(related, list):
                        program_refs.extend(str(item) for item in related if isinstance(item, str))
                    result_refs: set[str] = set()
                    for field_name in ("dependencyResultIds", "supersededByResultIds"):
                        references = value.get(field_name)
                        if isinstance(references, list):
                            result_refs.update(
                                str(item) for item in references if isinstance(item, str)
                            )
                    if not set(program_refs) <= readable["program"] or not result_refs <= readable["intermediateResult"]:
                        raise MathFlowError("research builder v10 result operation references unread state")
            operated.add(key)
    return operated


def apply_research_builder_v10_transition(
    base_state: dict[str, object],
    transition: dict[str, object],
    *,
    authoring_packet: Mapping[str, object],
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
) -> dict[str, object]:
    """Apply an already-expanded V9-compatible transition inside V10's scope."""

    state = validate_research_program_state_v3(copy.deepcopy(base_state))
    packet = validate_research_builder_v10_authoring_packet(
        copy.deepcopy(dict(authoring_packet)),
        base_state=state,
        accepted_claims=accepted_claims,
    )
    if transition.get("baseStateDigest") != packet["baseStateDigest"]:
        raise MathFlowError("research builder v10 transition has a stale packet binding")
    operated = _operation_scope(state, transition, packet)
    reduced = apply_research_builder_v9_transition(
        state,
        transition,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
    )
    post_state = reduced["postState"]
    assert isinstance(post_state, dict)
    for kind, collection_name in (
        ("program", "programs"),
        ("intermediateResult", "intermediateResults"),
    ):
        before = state[collection_name]
        after = post_state[collection_name]
        assert isinstance(before, dict) and isinstance(after, dict)
        for entity_id, record in before.items():
            if (kind, str(entity_id)) not in operated and after.get(entity_id) != record:
                raise MathFlowError("research builder v10 reducer changed hidden state")
    prior_contributions = state["contributions"]
    post_contributions = post_state["contributions"]
    assert isinstance(prior_contributions, dict) and isinstance(post_contributions, dict)
    if any(post_contributions.get(key) != value for key, value in prior_contributions.items()):
        raise MathFlowError("research builder v10 reducer changed prior contribution history")
    return {**reduced, "authoringPacketDigest": packet["authoringPacketDigest"]}


def run_research_builder_v10_two_stage(
    *,
    base_state: dict[str, object],
    accepted_claims: object,
    judgment_id: str,
    evidence_file_refs: Mapping[str, str],
    router: Callable[[dict[str, object]], object],
    author: Callable[[dict[str, object]], dict[str, object]],
    max_programs: int = 64,
    max_results: int = 64,
) -> dict[str, object]:
    """Provider-agnostic route-then-author reference orchestration.

    Tests and experiments can inject deterministic fake callbacks. A future
    governed provider adapter can bind each callback to its own sealed request.
    """

    route_context = build_research_builder_v10_route_context(base_state, accepted_claims)
    raw_plan = router(copy.deepcopy(route_context))
    packet = build_research_builder_v10_authoring_packet(
        base_state,
        accepted_claims,
        raw_plan,
        route_context=route_context,
        max_programs=max_programs,
        max_results=max_results,
    )
    transition = author(copy.deepcopy(packet))
    if not isinstance(transition, dict):
        raise MathFlowError("research builder v10 author did not return a transition")
    reduced = apply_research_builder_v10_transition(
        base_state,
        transition,
        authoring_packet=packet,
        accepted_claims=accepted_claims,
        judgment_id=judgment_id,
        evidence_file_refs=evidence_file_refs,
    )
    return {
        "routeContext": route_context,
        "routePlan": packet["routePlan"],
        "authoringPacket": packet,
        "transition": transition,
        "reduced": reduced,
    }


__all__ = [
    "apply_research_builder_v10_transition",
    "bind_research_builder_v10_route_plan",
    "build_research_builder_v10_authoring_packet",
    "build_research_builder_v10_catalog",
    "build_research_builder_v10_program_capsule",
    "build_research_builder_v10_route_context",
    "run_research_builder_v10_two_stage",
    "search_research_builder_v10_catalog",
    "validate_research_builder_v10_authoring_packet",
    "validate_research_builder_v10_catalog",
    "validate_research_builder_v10_route_context",
]
