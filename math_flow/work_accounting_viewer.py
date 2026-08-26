"""Deterministic, inactive viewer export for committed work accounting V1.

This module is deliberately not discovered or admitted by the published
projection catalog. It is the provider-free boundary between the accounting
scheduler/published bundle artifacts and an explicit future viewer admission
path.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from pathlib import Path

from .errors import MathFlowError
from .repository import sha256_json
from .research_topology import validate_research_program_state_versioned
from .work_accounting import (
    validate_root_contract,
    validate_submission_work_value,
    validate_work_accounting_state,
)
from .work_accounting_schedule import (
    validate_work_accounting_publication_manifest,
    validate_work_accounting_schedule,
    validate_work_accounting_state_repair,
)
from .work_projection import load_work_projection_bundle


UNIT = {
    "id": "competent-human-researcher-hour",
    "label": "competent human researcher hours",
    "storedValues": "canonical-decimal-hours",
    "displayShares": "derived-from-exact-values",
}


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
        committed_state = validate_work_accounting_state(
            loaded.get("withAccessState"), after_knowledge, bundle_contract
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
            or evaluation["withAccessStateDigest"] != committed_state["stateDigest"]
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
        evaluations.append(
            {
                "subjectTransactionId": subject,
                "canonicalOrdinal": record["ledgerOrdinal"],
                "evaluationDigest": evaluation["evaluationDigest"],
                "publicationManifestDigest": publication["publicationManifestDigest"],
                "committedAccountingStateDigest": committed_state["stateDigest"],
                "exAnteWorkHours": evaluation["noAccessWorkHours"],
                "exPostWorkHours": evaluation["withAccessWorkHours"],
                "workReductionHours": evaluation["workValueHours"],
                "nodeAnnotations": _annotation_view(
                    committed_state, evaluation["affectedNodeRefs"]
                ),
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
        "scheduleDigest": current["scheduleDigest"],
        "inputStatus": "exact-committed",
        "stale": False,
        "staleReasons": [],
    }
    run["viewerDigest"] = _digest(run, "viewerDigest")
    return {
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

    loaded = [load_work_projection_bundle(Path(path)) for path in evaluation_bundle_dirs]
    return build_work_accounting_viewer_projection(
        loaded_evaluation_bundles=loaded,
        **kwargs,
    )
