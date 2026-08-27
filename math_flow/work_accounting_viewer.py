"""Deterministic V2 viewer export for committed work-accounting V1 lanes."""

from __future__ import annotations

import copy
import json
import tempfile
from collections.abc import Mapping, Sequence
from fractions import Fraction
from pathlib import Path, PurePosixPath

from .errors import MathFlowError
from .repository import sha256_json
from .research_topology import validate_research_program_state_versioned
from .work_accounting import (
    canonical_decimal,
    validate_root_contract,
    validate_submission_work_value,
    validate_work_accounting_patch,
    validate_work_accounting_state,
)
from .work_accounting_schedule import (
    validate_work_accounting_publication_manifest,
    validate_work_accounting_schedule,
    validate_work_accounting_state_repair,
)
from .work_accounting_pipeline import (
    materialize_stored_work_projection_bundle,
)
from .work_accounting_projection_store import (
    ProjectionBranchWorkAccountingStore,
    work_accounting_lane_scope_digest,
)
from .work_projection import (
    load_work_projection_bundle,
    validate_work_projection_request,
)


UNIT = {
    "id": "competent-human-researcher-hour",
    "label": "competent human researcher hours",
    "storedValues": "canonical-decimal-hours",
    "displayShares": "derived-from-exact-values",
}

RATIONALE_PREVIEW_LENGTH = 240
EVIDENCE_REF_PREVIEW_LENGTH = 160
EVIDENCE_REF_PREVIEW_COUNT = 3


def _digest(value: Mapping[str, object], field: str) -> str:
    return f"sha256:{sha256_json({key: copy.deepcopy(item) for key, item in value.items() if key != field})}"


def _node_key(value: object) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise MathFlowError("work-accounting viewer node reference must be an object")
    kind = value.get("kind")
    node_id = value.get("id")
    if kind not in {"program", "thread"} or not isinstance(node_id, str):
        raise MathFlowError(
            "work-accounting viewer numeric nodes must be programs or threads"
        )
    return str(kind), node_id


def _same_lane(
    value: Mapping[str, object], schedule: Mapping[str, object], *, label: str
) -> None:
    fields = ("problemId", "projectionId", "projectionSpecDigest", "rootContractDigest")
    if any(value.get(field) != schedule.get(field) for field in fields):
        raise MathFlowError(f"{label} belongs to another work-accounting lane")


def _annotation_view(
    state: Mapping[str, object], affected_refs: Sequence[object]
) -> list[dict[str, object]]:
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
    result: list[dict[str, object]] = []
    keys = [_node_key(item) for item in affected_refs]
    if keys != sorted(set(keys)):
        raise MathFlowError(
            "work-accounting viewer affected node references are not canonical"
        )
    for key in keys:
        annotation = annotations.get(key)
        computed = derived.get(key)
        if annotation is None or computed is None:
            raise MathFlowError(
                "work-accounting viewer evaluation references an unaccounted node"
            )
        result.append(
            {
                "nodeRef": copy.deepcopy(annotation["nodeRef"]),
                "knowledgeNodeDigest": annotation["knowledgeNodeDigest"],
                "directWorkHours": annotation["directWorkHours"],
                "conditionalIncidence": annotation["conditionalIncidence"],
                "globalReach": computed["globalReach"],
                "conditionalSubtreeWorkHours": computed["conditionalSubtreeWork"],
                "expectedDirectWorkHours": computed["expectedDirectWork"],
            }
        )
    return result


def _signed_decimal(value: Fraction) -> str:
    if value < 0:
        return f"-{canonical_decimal(-value)}"
    return canonical_decimal(value)


def _state_node_views(
    state: Mapping[str, object], knowledge_state: Mapping[str, object]
) -> dict[tuple[str, str], dict[str, object]]:
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
    knowledge_nodes: dict[tuple[str, str], Mapping[str, object]] = {}
    for kind, collection_name in (("program", "programs"), ("thread", "threads")):
        collection = knowledge_state[collection_name]
        assert isinstance(collection, dict)
        for node_id, record in collection.items():
            assert isinstance(record, dict)
            knowledge_nodes[(kind, str(node_id))] = record
    if set(annotations) != set(derived) or set(annotations) != set(knowledge_nodes):
        raise MathFlowError(
            "work-accounting viewer state does not cover the target knowledge topology"
        )
    return {
        key: {
            "nodeRef": copy.deepcopy(annotation["nodeRef"]),
            "knowledgeNodeDigest": annotation["knowledgeNodeDigest"],
            "knowledgeStatus": knowledge_nodes[key]["status"],
            "directWorkHours": annotation["directWorkHours"],
            "conditionalIncidence": annotation["conditionalIncidence"],
            "globalReach": derived[key]["globalReach"],
            "conditionalSubtreeWorkHours": derived[key]["conditionalSubtreeWork"],
            "expectedDirectWorkHours": derived[key]["expectedDirectWork"],
        }
        for key, annotation in annotations.items()
    }


def _patch_update_index(
    patch: Mapping[str, object],
) -> dict[tuple[str, str], dict[str, object]]:
    return {
        _node_key(item["nodeRef"]): copy.deepcopy(item)
        for item in patch["updates"]
        if isinstance(item, dict)
    }


def _topology_required_index(
    request: Mapping[str, object], *, label: str
) -> dict[tuple[str, str], dict[str, list[str]]]:
    """Read the exact topology contract already verified for one branch."""

    raw_required = request.get("requiredPrimitiveUpdates")
    if not isinstance(raw_required, list):
        raise MathFlowError(f"work-accounting viewer {label} request has no requirements")
    result: dict[tuple[str, str], dict[str, list[str]]] = {}
    prior: tuple[str, str] | None = None
    for raw in raw_required:
        if not isinstance(raw, dict):
            raise MathFlowError(
                f"work-accounting viewer {label} requirement is invalid"
            )
        key = _node_key(raw.get("nodeRef"))
        changes = raw.get("requiredChanges")
        reasons = raw.get("reasons")
        if (
            prior is not None
            and prior >= key
            or not isinstance(changes, list)
            or not changes
            or changes != sorted(set(changes))
            or not set(changes) <= {"directWorkHours", "conditionalIncidence"}
            or not isinstance(reasons, list)
            or not reasons
            or reasons != sorted(set(reasons))
            or not set(reasons) <= {"created", "reparented", "inactive-zeroing"}
        ):
            raise MathFlowError(
                f"work-accounting viewer {label} requirements are not canonical"
            )
        result[key] = {
            "requiredChanges": copy.deepcopy(changes),
            "reasons": copy.deepcopy(reasons),
        }
        prior = key
    return result


def _preview(value: str, maximum: int) -> tuple[str, bool]:
    return value[:maximum], len(value) > maximum


def _patch_view(update: Mapping[str, object] | None) -> dict[str, object] | None:
    if update is None:
        return None
    rationale = str(update["rationale"])
    rationale_preview, rationale_truncated = _preview(
        rationale, RATIONALE_PREVIEW_LENGTH
    )
    evidence_refs = [str(value) for value in update["evidenceRefs"]]
    evidence_previews: list[str] = []
    evidence_truncated = len(evidence_refs) > EVIDENCE_REF_PREVIEW_COUNT
    for value in evidence_refs[:EVIDENCE_REF_PREVIEW_COUNT]:
        preview, truncated = _preview(value, EVIDENCE_REF_PREVIEW_LENGTH)
        evidence_previews.append(preview)
        evidence_truncated = evidence_truncated or truncated
    return {
        "changes": copy.deepcopy(update["changes"]),
        "rationalePreview": rationale_preview,
        "rationaleTruncated": rationale_truncated,
        "evidenceRefPreviews": evidence_previews,
        "evidenceRefCount": len(evidence_refs),
        "evidenceRefsTruncated": evidence_truncated,
    }


def _node_effect_view(
    *,
    evaluation_digest: str,
    no_access_state: Mapping[str, object],
    new_live_state: Mapping[str, object],
    no_access_patch: Mapping[str, object],
    new_live_patch: Mapping[str, object],
    no_access_request: Mapping[str, object],
    new_live_request: Mapping[str, object],
    after_knowledge: Mapping[str, object],
    expected_work_reduction: str,
) -> tuple[list[dict[str, object]], str]:
    no_views = _state_node_views(no_access_state, after_knowledge)
    live_views = _state_node_views(new_live_state, after_knowledge)
    if set(no_views) != set(live_views):
        raise MathFlowError("work-accounting counterfactual node sets differ")
    no_updates = _patch_update_index(no_access_patch)
    live_updates = _patch_update_index(new_live_patch)
    direct_keys = set(no_updates) | set(live_updates)
    no_topology = _topology_required_index(no_access_request, label="no-access")
    live_topology = _topology_required_index(new_live_request, label="new-live")
    for requirements, updates in (
        (no_topology, no_updates),
        (live_topology, live_updates),
    ):
        for key, requirement in requirements.items():
            update = updates.get(key)
            if update is None or not set(requirement["requiredChanges"]) <= set(
                update["changes"]
            ):
                raise MathFlowError(
                    "work-accounting viewer topology requirement is absent from its patch"
                )
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
        live_view = live_views[key]
        primitive_differences = sorted(
            field for field in primitive_fields if no_view[field] != live_view[field]
        )
        derived_differences = sorted(
            field for field in derived_fields if no_view[field] != live_view[field]
        )
        is_direct = key in direct_keys
        if not is_direct and not derived_differences:
            continue
        direct_branches = []
        if key in no_updates:
            direct_branches.append("no-access")
        if key in live_updates:
            direct_branches.append("new-live")
        topology_branches = []
        topology_reasons: set[str] = set()
        topology_requirements: list[dict[str, object]] = []
        if key in no_topology:
            topology_branches.append("no-access")
            topology_reasons.update(no_topology[key]["reasons"])
            topology_requirements.append(
                {"branch": "no-access", **copy.deepcopy(no_topology[key])}
            )
        if key in live_topology:
            topology_branches.append("new-live")
            topology_reasons.update(live_topology[key]["reasons"])
            topology_requirements.append(
                {"branch": "new-live", **copy.deepcopy(live_topology[key])}
            )
        discretionary_fields = False
        for update, requirements in (
            (no_updates.get(key), no_topology.get(key)),
            (live_updates.get(key), live_topology.get(key)),
        ):
            if update is None:
                continue
            required_changes = (
                set(requirements["requiredChanges"])
                if requirements is not None
                else set()
            )
            if not set(update["changes"]) <= required_changes:
                discretionary_fields = True
        topology_only = bool(topology_requirements) and not discretionary_fields
        topology_classification = (
            "topology-only"
            if topology_only
            else "topology-associated"
            if topology_requirements
            else "none"
        )
        reduction = Fraction(str(no_view["expectedDirectWorkHours"])) - Fraction(
            str(live_view["expectedDirectWorkHours"])
        )
        additive_total += reduction
        effects.append(
            {
                "nodeRef": copy.deepcopy(no_view["nodeRef"]),
                "knowledgeNodeDigest": no_view["knowledgeNodeDigest"],
                "knowledgeStatus": no_view["knowledgeStatus"],
                "effectKind": "direct" if is_direct else "propagated",
                "directUpdateBranches": direct_branches,
                "topologyRequiredBranches": topology_branches,
                "topologyReasons": sorted(topology_reasons),
                "topologyRequirements": topology_requirements,
                "topologyClassification": topology_classification,
                "topologyOnly": topology_only,
                "primitiveDifferenceFields": primitive_differences,
                "derivedDifferenceFields": derived_differences,
                "noAccess": {
                    key: copy.deepcopy(value)
                    for key, value in no_view.items()
                    if key not in {"nodeRef", "knowledgeNodeDigest", "knowledgeStatus"}
                },
                "newLive": {
                    key: copy.deepcopy(value)
                    for key, value in live_view.items()
                    if key not in {"nodeRef", "knowledgeNodeDigest", "knowledgeStatus"}
                },
                "noAccessPatch": _patch_view(no_updates.get(key)),
                "newLivePatch": _patch_view(live_updates.get(key)),
                "workReductionHours": _signed_decimal(reduction),
            }
        )
    if additive_total != Fraction(expected_work_reduction):
        raise MathFlowError(
            "work-accounting viewer node effects do not sum to submission work value"
        )
    digest_value = {
        "evaluationDigest": evaluation_digest,
        "nodeEffects": effects,
    }
    return effects, f"sha256:{sha256_json(digest_value)}"


def _publication_index(
    publications: Sequence[object], schedule: Mapping[str, object]
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for raw in publications:
        publication = validate_work_accounting_publication_manifest(raw)
        _same_lane(publication, schedule, label="work-accounting publication")
        subject = str(publication["subjectTransactionId"])
        if subject in result:
            raise MathFlowError(
                "work-accounting viewer received duplicate publication manifests"
            )
        result[subject] = copy.deepcopy(publication)
    return result


def _repair_index(
    repairs: Sequence[object],
    repair_states: Sequence[object],
    *,
    schedule: Mapping[str, object],
    knowledge_state: Mapping[str, object],
    root_contract: Mapping[str, object],
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    events: dict[str, dict[str, object]] = {}
    for raw in repairs:
        event = validate_work_accounting_state_repair(raw)
        _same_lane(event, schedule, label="work-accounting repair")
        digest = str(event["repairEventDigest"])
        if digest in events:
            raise MathFlowError("work-accounting viewer received a duplicate repair event")
        events[digest] = copy.deepcopy(event)
    if set(events) != set(schedule["repairEventDigests"]):
        raise MathFlowError(
            "work-accounting viewer repair events do not exactly match the schedule"
        )

    states: dict[str, dict[str, object]] = {}
    for raw in repair_states:
        state = validate_work_accounting_state(raw, knowledge_state, root_contract)
        digest = str(state["stateDigest"])
        if digest in states:
            raise MathFlowError("work-accounting viewer received a duplicate repair state")
        states[digest] = copy.deepcopy(state)
    expected_states = {str(item["repairedAccountingStateDigest"]) for item in events.values()}
    if set(states) != expected_states:
        raise MathFlowError(
            "work-accounting viewer repair states do not exactly match the repair events"
        )
    return events, states


def _attach_verified_requests(
    loaded: Mapping[str, object], bundle_dir: Path
) -> dict[str, object]:
    """Attach the stored requests after the bundle loader has replayed them."""

    manifest = loaded.get("manifest")
    if not isinstance(manifest, dict):
        raise MathFlowError("work-accounting viewer verified bundle has no manifest")
    artifacts = manifest.get("artifacts")
    request_digests = manifest.get("requestDigests")
    if not isinstance(artifacts, list) or not isinstance(request_digests, list):
        raise MathFlowError("work-accounting viewer bundle request index is invalid")
    result = dict(loaded)
    seen_request_digests: set[str] = set()
    for output_key, role, stage in (
        ("noAccessRequest", "no-access-request", "no-access"),
        ("withAccessRequest", "with-access-request", "with-access"),
    ):
        matches = [
            item
            for item in artifacts
            if isinstance(item, dict) and item.get("role") == role
        ]
        if len(matches) != 1:
            raise MathFlowError(f"work-accounting viewer bundle must contain one {role}")
        relative = PurePosixPath(str(matches[0].get("path", "")))
        if relative.is_absolute() or not relative.parts or ".." in relative.parts:
            raise MathFlowError("work-accounting viewer bundle request path is unsafe")
        target = bundle_dir.resolve().joinpath(*relative.parts).resolve()
        try:
            target.relative_to(bundle_dir.resolve())
            raw = json.loads(target.read_bytes())
        except (ValueError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MathFlowError(
                "work-accounting viewer bundle request cannot be loaded"
            ) from exc
        request = validate_work_projection_request(raw)
        request_digest = str(request["requestDigest"])
        if (
            request["stage"] != stage
            or request_digest not in request_digests
            or request_digest in seen_request_digests
        ):
            raise MathFlowError("work-accounting viewer bundle request binding mismatch")
        seen_request_digests.add(request_digest)
        result[output_key] = request
    return result


def build_work_accounting_viewer_projection(
    *,
    projection_id: str,
    label: str,
    research_projection_ids: Sequence[str],
    schedule: object,
    loaded_evaluation_bundles: Sequence[Mapping[str, object]],
    publication_manifests: Sequence[object],
    terminal_accounting_state: object,
    terminal_knowledge_state: object,
    root_contract: object,
    repair_events: Sequence[object] = (),
    repair_accounting_states: Sequence[object] = (),
) -> dict[str, object]:
    """Build one exact viewer projection from already verified bundle contents.

    The per-submission evaluation bundle is the semantic source.  A schedule
    completion and publication manifest must independently bind that evaluation
    and its exact committed state before it is exported.
    """

    current = validate_work_accounting_schedule(schedule)
    contract = validate_root_contract(root_contract, str(current["problemId"]))
    knowledge = validate_research_program_state_versioned(
        terminal_knowledge_state, str(current["problemId"])
    )
    terminal = validate_work_accounting_state(
        terminal_accounting_state, knowledge, contract
    )
    if (
        current["rootContractDigest"] != contract["rootContractDigest"]
        or current["terminalKnowledgeStateDigest"] != knowledge["stateDigest"]
        or current["terminalAccountingStateDigest"] != terminal["stateDigest"]
    ):
        raise MathFlowError(
            "work-accounting viewer terminal artifacts do not match the schedule"
        )
    dependency_ids = list(research_projection_ids)
    if (
        not projection_id
        or not label
        or not dependency_ids
        or dependency_ids != sorted(set(dependency_ids))
        or any(not isinstance(item, str) or not item for item in dependency_ids)
    ):
        raise MathFlowError(
            "work-accounting viewer projection identity is not canonical"
        )

    publications = _publication_index(publication_manifests, current)
    records = {str(item["transactionId"]): item for item in current["subjects"]}
    evaluated_records = [
        item
        for item in current["subjects"]
        if isinstance(item.get("completion"), dict)
        and item["completion"].get("kind") == "evaluated"
    ]
    expected_subjects = {str(item["transactionId"]) for item in evaluated_records}
    if set(publications) != expected_subjects:
        raise MathFlowError(
            "work-accounting viewer publications do not exactly cover evaluated subjects"
        )

    bundles: dict[str, Mapping[str, object]] = {}
    for loaded in loaded_evaluation_bundles:
        manifest = loaded.get("manifest")
        if not isinstance(manifest, dict):
            raise MathFlowError("work-accounting viewer bundle has no verified manifest")
        subject = manifest.get("subjectTransactionId")
        if not isinstance(subject, str) or subject in bundles:
            raise MathFlowError(
                "work-accounting viewer bundles have invalid or duplicate subjects"
            )
        bundles[subject] = loaded
    if set(bundles) != expected_subjects:
        raise MathFlowError(
            "work-accounting viewer bundles do not exactly cover evaluated subjects"
        )

    evaluations: list[dict[str, object]] = []
    state_cursor = str(current["initialAccountingStateDigest"])
    for record in evaluated_records:
        subject = str(record["transactionId"])
        loaded = bundles[subject]
        publication = publications[subject]
        manifest = loaded["manifest"]
        evaluation = validate_submission_work_value(loaded.get("evaluation"))
        before_knowledge = validate_research_program_state_versioned(
            loaded.get("baseKnowledgeState"), str(current["problemId"])
        )
        after_knowledge = validate_research_program_state_versioned(
            loaded.get("targetKnowledgeState"), str(current["problemId"])
        )
        bundle_contract = validate_root_contract(
            loaded.get("rootContract"), str(current["problemId"])
        )
        base_state = validate_work_accounting_state(
            loaded.get("baseAccountingState"), before_knowledge, bundle_contract
        )
        no_access_patch = validate_work_accounting_patch(
            loaded.get("noAccessPatch")
        )
        new_live_patch = validate_work_accounting_patch(
            loaded.get("withAccessPatch")
        )
        no_access_state = validate_work_accounting_state(
            loaded.get("noAccessState"), after_knowledge, bundle_contract
        )
        committed_state = validate_work_accounting_state(
            loaded.get("withAccessState"), after_knowledge, bundle_contract
        )
        no_access_request = loaded.get("noAccessRequest")
        new_live_request = loaded.get("withAccessRequest")
        if not isinstance(no_access_request, dict) or not isinstance(
            new_live_request, dict
        ):
            raise MathFlowError(
                "work-accounting viewer bundle has no verified branch requests"
            )
        completion = record["completion"]
        assert isinstance(completion, dict)
        if (
            bundle_contract != contract
            or manifest.get("problemId") != current["problemId"]
            or manifest.get("subjectTransactionId") != subject
            or evaluation["subjectTransactionId"] != subject
            or base_state["stateDigest"] != state_cursor
            or evaluation["baseAccountingStateDigest"] != state_cursor
            or evaluation["noAccessPatchDigest"] != no_access_patch["patchDigest"]
            or evaluation["withAccessPatchDigest"] != new_live_patch["patchDigest"]
            or evaluation["noAccessStateDigest"] != no_access_state["stateDigest"]
            or evaluation["withAccessStateDigest"] != committed_state["stateDigest"]
            or no_access_patch["evaluationMode"] != "no-access"
            or new_live_patch["evaluationMode"] != "with-access"
            or no_access_state["evaluationMode"] != "no-access"
            or committed_state["evaluationMode"] != "with-access"
            or after_knowledge["stateDigest"] != record["postKnowledgeStateDigest"]
            or after_knowledge["ledgerHead"] != record["postKnowledgeLedgerHead"]
            or publication["ledgerOrdinal"] != record["ledgerOrdinal"]
            or publication["attemptNumber"] != completion["attemptNumber"]
            or publication["evaluationDigest"] != evaluation["evaluationDigest"]
            or publication["committedAccountingStateDigest"]
            != committed_state["stateDigest"]
            or publication["workValueHours"] != evaluation["workValueHours"]
            or publication["publicationManifestDigest"]
            != completion["publicationManifestDigest"]
            or evaluation["evaluationDigest"] != completion["evaluationDigest"]
            or committed_state["stateDigest"]
            != completion["committedAccountingStateDigest"]
        ):
            raise MathFlowError(
                "work-accounting viewer evaluation is not the schedule's exact publication"
            )
        for field in (
            "rootContractDigest",
            "predecessorAccountingStateDigest",
            "predecessorKnowledgeStateDigest",
            "postKnowledgeStateDigest",
            "noAccessPatchDigest",
            "withAccessPatchDigest",
            "noAccessStateDigest",
        ):
            expected_field = {
                "predecessorAccountingStateDigest": "baseAccountingStateDigest",
                "predecessorKnowledgeStateDigest": "baseKnowledgeStateDigest",
                "postKnowledgeStateDigest": "targetKnowledgeStateDigest",
            }.get(field, field)
            if publication[field] != evaluation.get(expected_field):
                raise MathFlowError(
                    f"work-accounting viewer publication {field} binding mismatch"
                )

        affected_repairs = list(record["affectedByRepairDigests"])
        node_effects, node_effects_digest = _node_effect_view(
            evaluation_digest=str(evaluation["evaluationDigest"]),
            no_access_state=no_access_state,
            new_live_state=committed_state,
            no_access_patch=no_access_patch,
            new_live_patch=new_live_patch,
            no_access_request=no_access_request,
            new_live_request=new_live_request,
            after_knowledge=after_knowledge,
            expected_work_reduction=str(evaluation["workValueHours"]),
        )
        direct_update_count = sum(
            item["effectKind"] == "direct" for item in node_effects
        )
        propagated_effect_count = sum(
            item["effectKind"] == "propagated" for item in node_effects
        )
        evaluations.append(
            {
                "subjectTransactionId": subject,
                "canonicalOrdinal": record["ledgerOrdinal"],
                "evaluationDigest": evaluation["evaluationDigest"],
                "publicationManifestDigest": publication["publicationManifestDigest"],
                "committedAccountingStateDigest": committed_state["stateDigest"],
                "noAccessWorkHours": evaluation["noAccessWorkHours"],
                "newLiveWorkHours": evaluation["withAccessWorkHours"],
                "exAnteWorkHours": evaluation["noAccessWorkHours"],
                "exPostWorkHours": evaluation["withAccessWorkHours"],
                "workReductionHours": evaluation["workValueHours"],
                "nodeAnnotations": _annotation_view(
                    committed_state, evaluation["affectedNodeRefs"]
                ),
                "directUpdateCount": direct_update_count,
                "propagatedEffectCount": propagated_effect_count,
                "topologyOnlyCount": sum(
                    bool(item["topologyOnly"]) for item in node_effects
                ),
                "nodeEffectsDigest": node_effects_digest,
                "nodeEffects": node_effects,
                "prospectiveCorrection": bool(affected_repairs),
                "affectedHistory": bool(affected_repairs),
                "affectedByRepairDigests": affected_repairs,
                "evaluation": copy.deepcopy(evaluation),
            }
        )
        state_cursor = str(committed_state["stateDigest"])

    events, repair_states = _repair_index(
        repair_events,
        repair_accounting_states,
        schedule=current,
        knowledge_state=knowledge,
        root_contract=contract,
    )
    ordered_repairs: list[dict[str, object]] = []
    unused = dict(events)
    while unused:
        matches = [
            item
            for item in unused.values()
            if item["baseAccountingStateDigest"] == state_cursor
        ]
        if len(matches) != 1:
            raise MathFlowError(
                "work-accounting viewer repair lineage is incomplete or ambiguous"
            )
        event = matches[0]
        repaired = repair_states[str(event["repairedAccountingStateDigest"])]
        if repaired["predecessorStateDigest"] != state_cursor:
            raise MathFlowError(
                "work-accounting viewer repair state has a stale predecessor"
            )
        ordered_repairs.append(copy.deepcopy(event))
        state_cursor = str(repaired["stateDigest"])
        del unused[str(event["repairEventDigest"])]
    if state_cursor != terminal["stateDigest"]:
        raise MathFlowError(
            "work-accounting viewer committed state chain does not reach the terminal state"
        )

    event_by_digest = {str(item["repairEventDigest"]): item for item in ordered_repairs}
    evaluation_by_subject = {
        str(item["subjectTransactionId"]): item for item in evaluations
    }
    for subject, record in records.items():
        expected_flags = list(record["affectedByRepairDigests"])
        for repair_digest in expected_flags:
            event = event_by_digest.get(str(repair_digest))
            if event is None or not any(
                flag["subjectTransactionId"] == subject
                and flag["evaluationDigest"]
                == (
                    evaluation_by_subject[subject]["evaluationDigest"]
                    if subject in evaluation_by_subject
                    else None
                )
                for flag in event["affectedHistory"]
            ):
                raise MathFlowError(
                    "work-accounting viewer repair flags do not match affected history"
                )
    for event in ordered_repairs:
        repair_digest = str(event["repairEventDigest"])
        for flag in event["affectedHistory"]:
            subject = str(flag["subjectTransactionId"])
            record = records.get(subject)
            if (
                record is None
                or repair_digest not in record["affectedByRepairDigests"]
                or flag["evaluationDigest"]
                != (
                    evaluation_by_subject[subject]["evaluationDigest"]
                    if subject in evaluation_by_subject
                    else None
                )
            ):
                raise MathFlowError(
                    "work-accounting viewer affected history is not reciprocally flagged"
                )

    run: dict[str, object] = {
        "id": current["scheduleDigest"],
        "runDigest": current["scheduleDigest"],
        "problemId": current["problemId"],
        "projectionId": current["projectionId"],
        "projectionSpecDigest": current["projectionSpecDigest"],
        "rootContractDigest": current["rootContractDigest"],
        "problemLedgerDigest": current["problemLedgerDigest"],
        "terminalKnowledgeStateDigest": current["terminalKnowledgeStateDigest"],
        "terminalAccountingStateDigest": current["terminalAccountingStateDigest"],
        "unit": copy.deepcopy(UNIT),
        "evaluations": evaluations,
        "repairs": ordered_repairs,
        "terminalAccountingState": copy.deepcopy(terminal),
        "terminalNodeAnnotations": [
            value
            for _, value in sorted(
                _state_node_views(terminal, knowledge).items()
            )
        ],
        "scheduleDigest": current["scheduleDigest"],
        "inputStatus": "exact-committed",
        "stale": False,
        "staleReasons": [],
    }
    run["viewerDigest"] = _digest(run, "viewerDigest")
    return {
        "schemaVersion": 2,
        "id": projection_id,
        "problemId": current["problemId"],
        "label": label,
        "researchProjectionIds": dependency_ids,
        "latestRunDigest": run["runDigest"],
        "selectionStatus": "current",
        "runCount": 1,
        "runs": [run],
        "workAccounting": copy.deepcopy(UNIT),
    }


def load_work_accounting_viewer_projection(
    *,
    evaluation_bundle_dirs: Sequence[Path],
    **kwargs: object,
) -> dict[str, object]:
    """Verify bundle directories, then build the inactive viewer projection."""

    loaded = [
        _attach_verified_requests(load_work_projection_bundle(Path(path)), Path(path))
        for path in evaluation_bundle_dirs
    ]
    return build_work_accounting_viewer_projection(
        loaded_evaluation_bundles=loaded,
        **kwargs,
    )


def _stored_json(
    store: ProjectionBranchWorkAccountingStore, key: str, label: str
) -> dict[str, object]:
    stored = store.get(key)
    if stored is None:
        raise MathFlowError(f"published work-accounting {label} is missing")
    try:
        value = json.loads(stored.value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(
            f"published work-accounting {label} is not valid JSON"
        ) from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"published work-accounting {label} must be an object")
    return value


def _digest_key(kind: str, digest: str) -> str:
    return f"objects/{kind}/{digest.removeprefix('sha256:')}.json"


def load_published_work_accounting_viewer_projection(
    store: ProjectionBranchWorkAccountingStore,
    *,
    label: str,
    research_projection_ids: Sequence[str],
) -> dict[str, object]:
    """Reconstruct a viewer projection solely from one verified published CAS lane."""

    snapshot = store.load_published_snapshot()
    if snapshot is None:
        raise MathFlowError("published work-accounting lane has no publication marker")
    pipeline = snapshot["pipeline"]
    completed = pipeline["completedTransitions"]
    if not completed:
        raise MathFlowError("published work-accounting lane has no evaluated submissions")
    schedule = validate_work_accounting_schedule(
        _stored_json(
            store,
            _digest_key("schedules", str(pipeline["scheduleDigest"])),
            "schedule",
        )
    )
    if schedule["repairEventDigests"]:
        raise MathFlowError(
            "published work-accounting repair export requires explicit repair artifacts"
        )
    contract = validate_root_contract(
        _stored_json(
            store,
            _digest_key("root-contracts", str(pipeline["rootContractDigest"])),
            "root contract",
        ),
        str(pipeline["problemId"]),
    )
    terminal_knowledge = validate_research_program_state_versioned(
        _stored_json(
            store,
            _digest_key(
                "knowledge-states", str(schedule["terminalKnowledgeStateDigest"])
            ),
            "terminal knowledge state",
        ),
        str(pipeline["problemId"]),
    )
    terminal_accounting = validate_work_accounting_state(
        _stored_json(
            store,
            _digest_key(
                "accounting-states", str(schedule["terminalAccountingStateDigest"])
            ),
            "terminal accounting state",
        ),
        terminal_knowledge,
        contract,
    )
    publications = [
        validate_work_accounting_publication_manifest(
            _stored_json(
                store,
                _digest_key(
                    "publication-manifests",
                    str(item["publicationManifestDigest"]),
                ),
                "submission publication manifest",
            )
        )
        for item in completed
    ]
    with tempfile.TemporaryDirectory() as temporary:
        bundle_root = Path(temporary)
        loaded_bundles = []
        for index, item in enumerate(completed, start=1):
            output_dir = bundle_root / f"bundle-{index:06d}"
            loaded_bundles.append(
                _attach_verified_requests(
                    materialize_stored_work_projection_bundle(
                        store,
                        bundle_digest=str(item["workBundleDigest"]),
                        output_dir=output_dir,
                    ),
                    output_dir,
                )
            )
        return build_work_accounting_viewer_projection(
            projection_id=store.projection_id,
            label=label,
            research_projection_ids=research_projection_ids,
            schedule=schedule,
            loaded_evaluation_bundles=loaded_bundles,
            publication_manifests=publications,
            terminal_accounting_state=terminal_accounting,
            terminal_knowledge_state=terminal_knowledge,
            root_contract=contract,
        )


def discover_published_work_accounting_viewer_projections(
    projection_root: Path,
    *,
    projection_specs: Mapping[str, Mapping[str, object]],
    problem_ids: Sequence[str],
) -> list[dict[str, object]]:
    """Discover only active governed lanes with an exact published marker."""

    results: list[dict[str, object]] = []
    for projection_digest, spec in sorted(projection_specs.items()):
        runner = spec.get("runner")
        dependencies = spec.get("dependencies")
        handoffs = (
            [
                item
                for item in dependencies
                if isinstance(item, dict)
                and item.get("artifactRole") == "research-builder-handoff"
            ]
            if isinstance(dependencies, list)
            else []
        )
        if (
            spec.get("engine") != "overlay-repository-v1"
            or not isinstance(runner, dict)
            or runner.get("implementation") != "openrouter-work-accounting-v1"
            or len(handoffs) != 1
        ):
            continue
        allowed = spec.get("allowedProblems")
        if not isinstance(allowed, list):
            raise MathFlowError("governed work-accounting problem allowlist is invalid")
        projection_id = str(spec["id"])
        for problem in sorted(set(problem_ids)):
            if "*" not in allowed and problem not in allowed:
                continue
            scope = work_accounting_lane_scope_digest(
                problem=problem,
                projection_id=projection_id,
                projection_spec_digest=projection_digest,
            ).removeprefix("sha256:")
            marker = (
                projection_root.resolve()
                / "indexes"
                / "problems"
                / problem
                / "work-accounting-v1"
                / scope
                / "publication.json"
            )
            if not marker.exists():
                continue
            if marker.is_symlink() or not marker.is_file():
                raise MathFlowError(
                    "published work-accounting marker is not a regular file"
                )
            store = ProjectionBranchWorkAccountingStore(
                projection_root,
                problem=problem,
                projection_id=projection_id,
                projection_spec_digest=projection_digest,
                create=False,
            )
            snapshot = store.load_published_snapshot()
            if snapshot is None or not snapshot["pipeline"]["completedTransitions"]:
                continue
            results.append(
                load_published_work_accounting_viewer_projection(
                    store,
                    label=projection_id,
                    research_projection_ids=[str(handoffs[0]["projectionId"])],
                )
            )
    results.sort(
        key=lambda item: (
            str(item["problemId"]),
            str(item["label"]),
            str(item["id"]),
        )
    )
    identities = [(str(item["problemId"]), str(item["id"])) for item in results]
    if len(identities) != len(set(identities)):
        raise MathFlowError(
            "published work-accounting lanes repeat a problem/projection identity"
        )
    return results
