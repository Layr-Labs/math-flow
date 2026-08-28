from __future__ import annotations

import copy
from collections import defaultdict

from .errors import MathFlowError
from .research_builder_v7 import validate_research_program_state_v3
from .repository import sha256_json
from .research_topology import validate_research_program_state_v2


SUPPORT_ITEM_TYPES = {"proof", "method", "computation", "tool"}
TARGET_STATE_FIELDS = {
    "schemaVersion",
    "problemId",
    "ledgerHead",
    "baseStateDigest",
    "rootProgramId",
    "programs",
    "intermediateResults",
    "contributions",
    "stateDigest",
}


def _digest_record(record: dict[str, object]) -> str:
    return f"sha256:{sha256_json({key: value for key, value in record.items() if key != 'digest'})}"


def _with_record_digest(record: dict[str, object]) -> dict[str, object]:
    value = copy.deepcopy(record)
    value.pop("digest", None)
    value["digest"] = _digest_record(value)
    return value


def _with_state_digest(state: dict[str, object]) -> dict[str, object]:
    value = copy.deepcopy(state)
    value.pop("stateDigest", None)
    value["stateDigest"] = f"sha256:{sha256_json(value)}"
    return value


def _support_text(item: dict[str, object]) -> str:
    return f"{item['title']}\n\n{item['summary']}"


def _thread_state_text(thread: dict[str, object]) -> str:
    parts = [str(thread["summary"]), f"Source thread status: {thread['status']}."]
    conditions = thread.get("conditions", [])
    if conditions:
        parts.append("Conditions: " + "; ".join(str(value) for value in conditions))
    exposure = str(thread.get("expectedExposure", "0"))
    if exposure != "0":
        parts.append(f"Legacy expected exposure: {exposure}.")
    return "\n\n".join(parts)


def _canonical_claim_refs(values: list[dict[str, object]]) -> list[dict[str, str]]:
    unique = {
        (str(value["transactionId"]), str(value["claimKey"])) for value in values
    }
    return [
        {"transactionId": transaction_id, "claimKey": claim_key}
        for transaction_id, claim_key in sorted(unique)
    ]


def _unresolved(
    reason_code: str,
    source_kind: str,
    source_ids: list[str],
    detail: str,
    *,
    candidate_result_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "reasonCode": reason_code,
        "sourceKind": source_kind,
        "sourceIds": sorted(source_ids),
        "candidateIntermediateResultIds": sorted(candidate_result_ids or []),
        "detail": detail,
    }


def _thread_program_plan(
    programs: dict[str, dict[str, object]],
    threads: dict[str, dict[str, object]],
) -> tuple[
    dict[str, str],
    list[dict[str, str]],
    list[dict[str, object]],
]:
    mapping: dict[str, str] = {}
    audit: list[dict[str, str]] = []
    unresolved: list[dict[str, object]] = []
    occupants: dict[str, list[str]] = defaultdict(list)
    for program_id, program in programs.items():
        for thread_id in program["parentThreadIds"]:
            occupants[str(thread_id)].append(program_id)

    for thread_id in sorted(threads):
        thread = threads[thread_id]
        if thread["kind"] == "unstructured":
            target_id = str(thread["programId"])
            mode = "local-residual"
        else:
            thread_occupants = sorted(occupants.get(thread_id, []))
            if len(thread_occupants) > 1:
                unresolved.append(
                    _unresolved(
                        "thread-has-multiple-program-occupants",
                        "thread",
                        [thread_id, *thread_occupants],
                        "A substantive source thread cannot be folded into more than one existing program without choosing a semantic successor.",
                    )
                )
                continue
            if thread_occupants:
                target_id = thread_occupants[0]
                mode = "existing-child-program"
            elif thread_id in programs:
                unresolved.append(
                    _unresolved(
                        "thread-program-id-collision",
                        "thread",
                        [thread_id],
                        "The substantive thread ID collides with an unrelated source program ID.",
                    )
                )
                continue
            else:
                target_id = thread_id
                mode = "promoted-program"
        mapping[thread_id] = target_id
        audit.append(
            {
                "sourceThreadId": thread_id,
                "targetProgramId": target_id,
                "mode": mode,
            }
        )
    return mapping, audit, unresolved


def _item_membership_plan(
    items: dict[str, dict[str, object]],
    contributions: dict[str, dict[str, object]],
) -> tuple[dict[str, str], list[dict[str, object]]]:
    memberships: dict[str, list[str]] = defaultdict(list)
    for contribution_id, contribution in contributions.items():
        for item_id in contribution["itemIds"]:
            memberships[str(item_id)].append(contribution_id)

    item_contribution: dict[str, str] = {}
    unresolved: list[dict[str, object]] = []
    for item_id in sorted(items):
        owners = sorted(memberships.get(item_id, []))
        if len(owners) != 1:
            unresolved.append(
                _unresolved(
                    "item-contribution-membership-not-unique",
                    "item",
                    [item_id, *owners],
                    "Every source item must belong to exactly one immutable contribution mapping before it can be folded losslessly.",
                )
            )
            continue
        item_contribution[item_id] = owners[0]
    return item_contribution, unresolved


def _support_anchor(
    support_id: str,
    items: dict[str, dict[str, object]],
    contribution: dict[str, object],
) -> tuple[str | None, dict[str, object] | None]:
    support = items[support_id]
    candidates = sorted(
        item_id
        for item_id in contribution["itemIds"]
        if items[str(item_id)]["type"] == "result"
    )
    if not candidates:
        return None, _unresolved(
            "support-without-result",
            "item",
            [support_id],
            "A proof, method, computation, or tool has no result anchor in its contribution mapping.",
        )
    if len(candidates) == 1:
        return candidates[0], None

    direct = sorted(
        result_id
        for result_id in candidates
        if support_id in items[result_id]["dependencyItemIds"]
        or result_id in support["dependencyItemIds"]
    )
    if len(direct) == 1:
        return direct[0], None
    if len(direct) > 1:
        return None, _unresolved(
            "support-linked-to-multiple-results",
            "item",
            [support_id],
            "Explicit dependency edges associate one support item with multiple result anchors.",
            candidate_result_ids=direct,
        )

    support_claims = {
        (reference["transactionId"], reference["claimKey"])
        for reference in support["claimRefs"]
    }
    claim_matches = sorted(
        result_id
        for result_id in candidates
        if support_claims
        and support_claims
        & {
            (reference["transactionId"], reference["claimKey"])
            for reference in items[result_id]["claimRefs"]
        }
    )
    if len(claim_matches) == 1:
        return claim_matches[0], None

    program_matches = sorted(
        result_id
        for result_id in candidates
        if items[result_id]["programId"] == support["programId"]
    )
    if len(program_matches) == 1:
        return program_matches[0], None

    return None, _unresolved(
        "ambiguous-support-result",
        "item",
        [support_id],
        "The source state does not identify which of several co-contributed results owns this support item.",
        candidate_result_ids=candidates,
    )


def _item_bundle_plan(
    items: dict[str, dict[str, object]],
    contributions: dict[str, dict[str, object]],
    item_contribution: dict[str, str],
) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, object]]]:
    item_to_result: dict[str, str] = {}
    audit: list[dict[str, str]] = []
    unresolved: list[dict[str, object]] = []

    for item_id in sorted(items):
        item = items[item_id]
        item_type = str(item["type"])
        contribution_id = item_contribution.get(item_id)
        if contribution_id is None:
            continue
        if item_type == "result":
            item_to_result[item_id] = item_id
            audit.append(
                {
                    "sourceItemId": item_id,
                    "targetIntermediateResultId": item_id,
                    "mode": "result-anchor",
                }
            )
            continue
        if item_type == "question":
            unresolved.append(
                _unresolved(
                    "question-item-requires-semantic-choice",
                    "item",
                    [item_id],
                    "A source question must become either a program direction or a result statement; state v2 does not decide which.",
                )
            )
            continue
        if item_type not in SUPPORT_ITEM_TYPES:
            unresolved.append(
                _unresolved(
                    "unsupported-item-type",
                    "item",
                    [item_id],
                    f"The two-entity migration does not recognize source item type {item_type!r}.",
                )
            )
            continue
        result_id, issue = _support_anchor(
            item_id, items, contributions[contribution_id]
        )
        if issue is not None:
            unresolved.append(issue)
            continue
        assert result_id is not None
        item_to_result[item_id] = result_id
        audit.append(
            {
                "sourceItemId": item_id,
                "targetIntermediateResultId": result_id,
                "mode": f"bundled-{item_type}",
            }
        )
    return item_to_result, audit, unresolved


def _bundled_dependency_cycle(
    items: dict[str, dict[str, object]], item_to_result: dict[str, str]
) -> list[str]:
    edges: dict[str, set[str]] = {
        result_id: set() for result_id in set(item_to_result.values())
    }
    for item_id, result_id in item_to_result.items():
        for dependency_item_id in items[item_id]["dependencyItemIds"]:
            dependency_result_id = item_to_result[str(dependency_item_id)]
            if dependency_result_id != result_id:
                edges[result_id].add(dependency_result_id)

    visiting: list[str] = []
    visited: set[str] = set()

    def visit(result_id: str) -> list[str]:
        if result_id in visited:
            return []
        if result_id in visiting:
            start = visiting.index(result_id)
            return [*visiting[start:], result_id]
        visiting.append(result_id)
        for dependency_id in sorted(edges[result_id]):
            cycle = visit(dependency_id)
            if cycle:
                return cycle
        visiting.pop()
        visited.add(result_id)
        return []

    for result_id in sorted(edges):
        cycle = visit(result_id)
        if cycle:
            return cycle
    return []


def _map_thread_status(status: str) -> str:
    if status == "completed":
        return "completed"
    if status == "retired":
        return "retired"
    return "active"


def _build_programs(
    source_programs: dict[str, dict[str, object]],
    threads: dict[str, dict[str, object]],
    thread_program_map: dict[str, str],
    thread_audit: list[dict[str, str]],
) -> dict[str, dict[str, object]]:
    modes = {record["sourceThreadId"]: record["mode"] for record in thread_audit}
    mapped_substantive: dict[str, list[dict[str, object]]] = defaultdict(list)
    residuals: dict[str, list[dict[str, object]]] = defaultdict(list)
    for thread_id, target_id in thread_program_map.items():
        thread = threads[thread_id]
        if modes[thread_id] == "local-residual":
            residuals[target_id].append(thread)
        elif modes[thread_id] == "existing-child-program":
            mapped_substantive[target_id].append(thread)

    programs: dict[str, dict[str, object]] = {}
    for program_id in sorted(source_programs):
        source = source_programs[program_id]
        source_threads = sorted(
            mapped_substantive.get(program_id, []), key=lambda value: str(value["id"])
        )
        residual_threads = sorted(
            residuals.get(program_id, []), key=lambda value: str(value["id"])
        )
        current_summary = (
            "\n\n".join(_thread_state_text(thread) for thread in source_threads)
            if source_threads
            else str(source["objective"])
        )
        local_summary = (
            "\n\n".join(_thread_state_text(thread) for thread in residual_threads)
            if residual_threads
            else "No explicit local residual work remains in the source state."
        )
        source_transactions = sorted(
            {
                *source["sourceTransactionIds"],
                *(
                    transaction_id
                    for thread in [*source_threads, *residual_threads]
                    for transaction_id in thread["sourceTransactionIds"]
                ),
            }
        )
        programs[program_id] = {
            "id": program_id,
            "parentId": source["parentId"],
            "title": source["title"],
            "objective": source["objective"],
            "currentStateSummary": current_summary,
            "localResidualSummary": local_summary,
            "status": source["status"],
            "intermediateResultIds": [],
            "sourceTransactionIds": source_transactions,
            "lineage": copy.deepcopy(source["lineage"]),
        }

    for thread_id in sorted(thread_program_map):
        if modes[thread_id] != "promoted-program":
            continue
        thread = threads[thread_id]
        summary = _thread_state_text(thread)
        programs[thread_id] = {
            "id": thread_id,
            "parentId": thread["programId"],
            "title": thread["title"],
            "objective": thread["summary"],
            "currentStateSummary": summary,
            "localResidualSummary": summary,
            "status": _map_thread_status(str(thread["status"])),
            "intermediateResultIds": [],
            "sourceTransactionIds": sorted(thread["sourceTransactionIds"]),
            "lineage": [],
        }
    return programs


def _build_intermediate_results(
    items: dict[str, dict[str, object]],
    contributions: dict[str, dict[str, object]],
    item_contribution: dict[str, str],
    item_to_result: dict[str, str],
    thread_program_map: dict[str, str],
) -> dict[str, dict[str, object]]:
    members: dict[str, list[str]] = defaultdict(list)
    for item_id, result_id in item_to_result.items():
        members[result_id].append(item_id)

    results: dict[str, dict[str, object]] = {}
    for result_id in sorted(members):
        anchor = items[result_id]
        member_ids = sorted(members[result_id])
        support: dict[str, object] = {
            "proofs": [],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactRefs": [],
            "attestationRefs": [],
        }
        for item_id in member_ids:
            if item_id == result_id:
                continue
            item_type = str(items[item_id]["type"])
            support[f"{item_type}s"].append(_support_text(items[item_id]))
        for key in ("proofs", "methods", "computations", "tools"):
            support[key] = sorted(set(support[key]))

        primary_program_id = str(anchor["programId"])
        related_program_ids: set[str] = set()
        claim_refs: list[dict[str, object]] = []
        source_transaction_ids: set[str] = set()
        judgment_ids: set[str] = set()
        dependency_result_ids: set[str] = set()
        for item_id in member_ids:
            item = items[item_id]
            owner_id = str(item["programId"])
            if owner_id != primary_program_id:
                related_program_ids.add(owner_id)
            claim_refs.extend(item["claimRefs"])
            source_transaction_ids.update(item["sourceTransactionIds"])
            contribution_id = item_contribution[item_id]
            contribution = contributions[contribution_id]
            judgment_ids.add(str(contribution["judgmentId"]))
            for thread_id in contribution["directThreadIds"]:
                target_program_id = thread_program_map[str(thread_id)]
                if target_program_id != primary_program_id:
                    related_program_ids.add(target_program_id)
            for dependency_id in item["dependencyItemIds"]:
                dependency_result_id = item_to_result[str(dependency_id)]
                if dependency_result_id != result_id:
                    dependency_result_ids.add(dependency_result_id)
        for transaction_id in source_transaction_ids:
            contribution = contributions.get(transaction_id)
            if contribution is not None:
                judgment_ids.add(str(contribution["judgmentId"]))

        results[result_id] = {
            "id": result_id,
            "primaryProgramId": primary_program_id,
            "relatedProgramIds": sorted(related_program_ids),
            "title": anchor["title"],
            "statement": anchor["summary"],
            "scopeQualifications": [],
            "support": support,
            "dependencyResultIds": sorted(dependency_result_ids),
            "claimRefs": _canonical_claim_refs(claim_refs),
            "sourceTransactionIds": sorted(source_transaction_ids),
            "judgmentIds": sorted(judgment_ids),
            "status": "active",
            "supersededByResultIds": [],
        }
    return results


def _build_contributions(
    contributions: dict[str, dict[str, object]],
    thread_program_map: dict[str, str],
    item_to_result: dict[str, str],
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for contribution_id in sorted(contributions):
        source = contributions[contribution_id]
        direct_program_ids = {
            str(source["directProgramId"]),
            *(thread_program_map[str(thread_id)] for thread_id in source["directThreadIds"]),
        }
        result[contribution_id] = _with_record_digest(
            {
                "id": contribution_id,
                "transactionId": source["transactionId"],
                "claimKeys": sorted(source["claimKeys"]),
                "directProgramIds": sorted(direct_program_ids),
                "intermediateResultIds": sorted(
                    {item_to_result[str(item_id)] for item_id in source["itemIds"]}
                ),
                "dependencyTransactionIds": sorted(source["dependencyTransactionIds"]),
                "judgmentId": source["judgmentId"],
            }
        )
    return result


def _validate_proposed_state_v3(value: dict[str, object]) -> None:
    if set(value) != TARGET_STATE_FIELDS or value.get("schemaVersion") != 3:
        raise MathFlowError("proposed two-entity state v3 has an invalid envelope")
    programs = value.get("programs")
    results = value.get("intermediateResults")
    contributions = value.get("contributions")
    if not isinstance(programs, dict) or not isinstance(results, dict) or not isinstance(contributions, dict):
        raise MathFlowError("proposed two-entity state v3 collections must be objects")
    for program_id, program in programs.items():
        if program.get("id") != program_id or program.get("digest") != _digest_record(program):
            raise MathFlowError(f"proposed two-entity program digest mismatch: {program_id}")
        parent_id = program.get("parentId")
        if parent_id is not None and parent_id not in programs:
            raise MathFlowError(f"proposed two-entity program has missing parent: {program_id}")
    expected_links: dict[str, set[str]] = {program_id: set() for program_id in programs}
    for result_id, intermediate_result in results.items():
        if intermediate_result.get("id") != result_id or intermediate_result.get("digest") != _digest_record(intermediate_result):
            raise MathFlowError(f"proposed intermediate-result digest mismatch: {result_id}")
        links = [intermediate_result.get("primaryProgramId"), *intermediate_result.get("relatedProgramIds", [])]
        if any(program_id not in programs for program_id in links):
            raise MathFlowError(f"proposed intermediate result has missing program: {result_id}")
        for program_id in links:
            expected_links[str(program_id)].add(result_id)
        if any(dependency_id not in results for dependency_id in intermediate_result.get("dependencyResultIds", [])):
            raise MathFlowError(f"proposed intermediate result has missing dependency: {result_id}")
    for program_id, program in programs.items():
        if program.get("intermediateResultIds") != sorted(expected_links[program_id]):
            raise MathFlowError(f"proposed program/result links are not reciprocal: {program_id}")
    for contribution_id, contribution in contributions.items():
        if contribution.get("id") != contribution_id or contribution.get("digest") != _digest_record(contribution):
            raise MathFlowError(f"proposed contribution digest mismatch: {contribution_id}")
        if any(program_id not in programs for program_id in contribution.get("directProgramIds", [])):
            raise MathFlowError(f"proposed contribution has missing direct program: {contribution_id}")
        if any(result_id not in results for result_id in contribution.get("intermediateResultIds", [])):
            raise MathFlowError(f"proposed contribution has missing intermediate result: {contribution_id}")
    if value.get("stateDigest") != _with_state_digest(value)["stateDigest"]:
        raise MathFlowError("proposed two-entity state v3 digest mismatch")
    # The audit's mapping checks are intentionally readable and localized, but
    # the emitted proposal must also pass the exact governed V3 contract.
    validate_research_program_state_v3(value, str(value["problemId"]))


def audit_two_entity_migration_v2(value: object) -> dict[str, object]:
    """Audit a state-v2 snapshot and return a deterministic, provider-free plan.

    ``proposedState`` is populated only when every source thread and item has an
    unambiguous mapping.  Callers can inspect ``unresolvedMappings`` without
    risking publication of a lossy partial state.
    """

    source = copy.deepcopy(validate_research_program_state_v2(value))
    programs = source["programs"]
    threads = source["threads"]
    items = source["items"]
    contributions = source["contributions"]
    assert isinstance(programs, dict)
    assert isinstance(threads, dict)
    assert isinstance(items, dict)
    assert isinstance(contributions, dict)

    thread_program_map, thread_mappings, unresolved = _thread_program_plan(
        programs, threads
    )
    item_contribution, membership_unresolved = _item_membership_plan(
        items, contributions
    )
    unresolved.extend(membership_unresolved)
    item_to_result, item_mappings, bundle_unresolved = _item_bundle_plan(
        items, contributions, item_contribution
    )
    unresolved.extend(bundle_unresolved)
    if len(item_to_result) == len(items):
        cycle = _bundled_dependency_cycle(items, item_to_result)
        if cycle:
            unresolved.append(
                _unresolved(
                    "dependency-cycle-after-bundling",
                    "intermediate-result",
                    cycle,
                    "Folding the selected support groups would turn the acyclic item graph into a cyclic result dependency graph.",
                    candidate_result_ids=cycle,
                )
            )
    unresolved = sorted(
        unresolved,
        key=lambda record: (
            str(record["reasonCode"]),
            tuple(record["sourceIds"]),
        ),
    )

    proposed_state: dict[str, object] | None = None
    if not unresolved:
        target_programs = _build_programs(
            programs, threads, thread_program_map, thread_mappings
        )
        target_results = _build_intermediate_results(
            items,
            contributions,
            item_contribution,
            item_to_result,
            thread_program_map,
        )
        for result_id, intermediate_result in target_results.items():
            for program_id in [
                intermediate_result["primaryProgramId"],
                *intermediate_result["relatedProgramIds"],
            ]:
                target_programs[str(program_id)]["intermediateResultIds"].append(
                    result_id
                )
        for program in target_programs.values():
            program["intermediateResultIds"] = sorted(
                set(program["intermediateResultIds"])
            )
        target_programs = {
            program_id: _with_record_digest(program)
            for program_id, program in sorted(target_programs.items())
        }
        target_results = {
            result_id: _with_record_digest(intermediate_result)
            for result_id, intermediate_result in sorted(target_results.items())
        }
        target_contributions = _build_contributions(
            contributions, thread_program_map, item_to_result
        )
        proposed_state = _with_state_digest(
            {
                "schemaVersion": 3,
                "problemId": source["problemId"],
                "ledgerHead": source["ledgerHead"],
                "baseStateDigest": None,
                "rootProgramId": "root",
                "programs": target_programs,
                "intermediateResults": target_results,
                "contributions": target_contributions,
            }
        )
        _validate_proposed_state_v3(proposed_state)

    audit: dict[str, object] = {
        "schemaVersion": 1,
        "migration": "research-program-state-v2-to-two-entity-v3",
        "sourceStateDigest": source["stateDigest"],
        "targetSchemaVersion": 3,
        "status": "ready" if proposed_state is not None else "unresolved",
        "summary": {
            "sourceProgramCount": len(programs),
            "sourceThreadCount": len(threads),
            "sourceItemCount": len(items),
            "sourceContributionCount": len(contributions),
            "promotedThreadProgramCount": sum(
                mapping["mode"] == "promoted-program" for mapping in thread_mappings
            ),
            "foldedResidualThreadCount": sum(
                mapping["mode"] == "local-residual" for mapping in thread_mappings
            ),
            "intermediateResultCount": len(
                {mapping["targetIntermediateResultId"] for mapping in item_mappings}
            ),
            "bundledSupportItemCount": sum(
                mapping["mode"].startswith("bundled-") for mapping in item_mappings
            ),
            "unresolvedMappingCount": len(unresolved),
        },
        "threadMappings": thread_mappings,
        "itemMappings": item_mappings,
        "unresolvedMappings": unresolved,
        "proposedState": proposed_state,
    }
    audit["auditDigest"] = f"sha256:{sha256_json(audit)}"
    return audit


def migrate_research_program_state_v2_to_v3(value: object) -> dict[str, object]:
    """Return a complete proposed v3 state or fail on any semantic ambiguity."""

    audit = audit_two_entity_migration_v2(value)
    proposed_state = audit["proposedState"]
    if not isinstance(proposed_state, dict):
        issues = audit["unresolvedMappings"]
        assert isinstance(issues, list)
        labels = [
            f"{issue['reasonCode']}:{','.join(issue['sourceIds'])}"
            for issue in issues[:5]
        ]
        suffix = "" if len(issues) <= 5 else f" (+{len(issues) - 5} more)"
        raise MathFlowError(
            "two-entity migration has unresolved mappings: "
            + "; ".join(labels)
            + suffix
        )
    return copy.deepcopy(proposed_state)
