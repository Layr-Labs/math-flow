from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .artifacts import ArtifactBundle, read_verified_artifact, sha256_bytes, verify_bundle
from .credit_schedule import plan_credit_run, validate_credit_run_schedule
from .errors import MathFlowError
from .governance import resolve_projection
from .hierarchical import _provider_run, _request, _structured_content
from .judges import load_judge_spec, load_source
from .judgments import load_judgment_bundle
from .openrouter import OpenRouterTransport, send_chat_completion
from .projection_dependencies import (
    projection_dependency_state_digest,
    resolve_projection_dependencies,
)
from .repository import read_at, sha256_json
from .research_projection import (
    _accepted_claims,
    _credit_policy,
    _credit_schema,
    _reject_truncated_response,
    _transaction_evidence,
    load_research_build_bundle,
)
from .research_state import (
    apply_research_program_batch_delta_v5,
    credit_child_thread_ids,
    credit_children,
    empty_research_program_state,
    materialize_credit_evaluations,
    validate_credit_against_program_state,
    validate_hierarchical_credit_state,
    validate_research_program_state,
)
from .runs import run_envelope


HIERARCHICAL_CREDIT_PROFILE = "math-flow/hierarchical-research-credit-v2"
_CREDIT_WORK_TEXT = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
_CREDIT_EFFECT_FIELDS = {
    "threadId",
    "withoutWork",
    "withWork",
    "rationale",
}
_CREDIT_CHILD_FIELDS = {
    "kind",
    "id",
    "counterfactual",
    "directEffects",
    "obviatedEffects",
    "confidence",
    "evidenceRefs",
}


def _published_bundle(
    projection_root: Path, run_kind: str, run_digest: str
) -> Path:
    digest_hex = run_digest.removeprefix("sha256:")
    target = (
        projection_root.resolve()
        / "objects"
        / run_kind
        / digest_hex[:2]
        / digest_hex
    )
    if not target.is_dir() or target.is_symlink():
        raise MathFlowError(f"hierarchical credit input is not published: {run_digest}")
    _, actual_digest = verify_bundle(target)
    if actual_digest != run_digest:
        raise MathFlowError(
            "hierarchical credit input does not match its content address"
        )
    return target


def _locked_research_state(
    projection_root: Path,
    dependency: dict[str, object],
    problem: str,
) -> tuple[Path, dict[str, object], dict[str, object], str]:
    if (
        dependency.get("artifactRole") != "research-program-state"
        or dependency.get("runKind") != "knowledge-build"
        or not isinstance(dependency.get("runDigest"), str)
    ):
        raise MathFlowError(
            "hierarchical credit requires one locked research-program-state dependency"
        )
    bundle = _published_bundle(
        projection_root, "knowledge-build", str(dependency["runDigest"])
    )
    manifest, state, run_digest = load_research_build_bundle(bundle)
    artifacts = manifest.get("artifacts")
    matching = [
        item
        for item in artifacts
        if isinstance(item, dict) and item.get("role") == "research-program-state"
    ] if isinstance(artifacts, list) else []
    if (
        manifest.get("problemId") != problem
        or manifest.get("problemLedgerDigest")
        != dependency.get("problemLedgerDigest")
        or len(matching) != 1
        or matching[0] != dependency.get("artifact")
    ):
        raise MathFlowError(
            "locked research-program state is inconsistent with its dependency record"
        )
    return bundle, manifest, state, run_digest


def _accepted_history(
    *,
    projection_root: Path,
    latest_run_digest: str,
    latest_state: dict[str, object],
) -> tuple[
    list[dict[str, object]],
    list[str],
    dict[tuple[str, str, str], tuple[dict[str, object], dict[str, object]]],
]:
    reverse_chain: list[
        tuple[Path, dict[str, object], dict[str, object], str]
    ] = []
    seen: set[str] = set()
    cursor: str | None = latest_run_digest
    while cursor is not None:
        if cursor in seen:
            raise MathFlowError("hierarchical research build history contains a cycle")
        seen.add(cursor)
        bundle = _published_bundle(projection_root, "knowledge-build", cursor)
        manifest, state, digest = load_research_build_bundle(bundle)
        reverse_chain.append((bundle, manifest, state, digest))
        base_run = manifest.get("baseRun")
        if base_run is not None and not isinstance(base_run, str):
            raise MathFlowError("hierarchical research build has an invalid base run")
        cursor = base_run
    chain = list(reversed(reverse_chain))
    if not chain or chain[-1][3] != latest_run_digest:
        raise MathFlowError("hierarchical research build history has the wrong terminal")

    problem = str(latest_state["problemId"])
    prior_state = empty_research_program_state(problem)
    prior_digest: str | None = None
    trace: list[dict[str, object]] = []
    history_run_digests: list[str] = []
    references: dict[
        tuple[str, str, str], tuple[dict[str, object], dict[str, object]]
    ] = {}
    accepted_transactions: set[str] = set()

    for bundle, manifest, post_state, run_digest in chain:
        if manifest.get("baseRun") != prior_digest:
            raise MathFlowError("hierarchical research build history is not one base-run chain")
        if post_state.get("problemId") != problem:
            raise MathFlowError("hierarchical research build history crosses problems")
        try:
            batch_input = json.loads(
                read_verified_artifact(bundle, manifest, "research-batch-input")
            )
            program_delta = json.loads(
                read_verified_artifact(bundle, manifest, "research-program-delta")
            )
        except json.JSONDecodeError as exc:
            raise MathFlowError(
                "hierarchical research build history contains invalid JSON"
            ) from exc
        judgments = batch_input.get("judgments") if isinstance(batch_input, dict) else None
        if not isinstance(judgments, list):
            raise MathFlowError("hierarchical research build history has invalid judgments")

        accepted_records: list[dict[str, object]] = []
        for batch_judgment in judgments:
            if not isinstance(batch_judgment, dict):
                raise MathFlowError("hierarchical research history has an invalid judgment")
            accepted_keys = batch_judgment.get("acceptedClaimKeys")
            if not isinstance(accepted_keys, list):
                raise MathFlowError(
                    "hierarchical research history has invalid accepted claim keys"
                )
            if not accepted_keys:
                continue
            judgment_run_digest = batch_judgment.get("runDigest")
            subject_id = batch_judgment.get("subjectTransactionId")
            if not isinstance(judgment_run_digest, str) or not isinstance(
                subject_id, str
            ):
                raise MathFlowError(
                    "hierarchical research history has incomplete accepted judgment metadata"
                )
            judgment_bundle = _published_bundle(
                projection_root, "judgment", judgment_run_digest
            )
            judgment_manifest, judgment, verified_judgment_digest = (
                load_judgment_bundle(judgment_bundle)
            )
            try:
                packet = json.loads(
                    read_verified_artifact(
                        judgment_bundle,
                        judgment_manifest,
                        "judgment-dependency-packet",
                    )
                )
            except json.JSONDecodeError as exc:
                raise MathFlowError(
                    "hierarchical credit history has an invalid validity packet"
                ) from exc
            accepted_claims = _accepted_claims(judgment, packet)
            if (
                verified_judgment_digest != judgment_run_digest
                or judgment.get("judgmentId") != batch_judgment.get("judgmentId")
                or packet.get("subjectTransactionId") != subject_id
                or sorted(str(claim["claimKey"]) for claim in accepted_claims)
                != sorted(str(key) for key in accepted_keys)
            ):
                raise MathFlowError(
                    "hierarchical credit history does not match its accepted validity record"
                )
            accepted_transactions.add(subject_id)
            accepted_records.append(
                {
                    "subjectTransactionId": subject_id,
                    "judgmentId": judgment["judgmentId"],
                    "judgmentRunDigest": judgment_run_digest,
                    "acceptedClaims": accepted_claims,
                    "validityAssessments": [
                        assessment
                        for assessment in judgment["assessments"]
                        if assessment.get("status") == "valid"
                    ],
                }
            )

        if manifest.get("outputProfile") == "math-flow/hierarchical-research-v5":
            if (
                batch_input.get("baseProgramStateDigest")
                != prior_state.get("stateDigest")
            ):
                raise MathFlowError(
                    "hierarchical research v5 history batch does not bind its prior state"
                )
            accepted_claims_by_transaction = {
                str(record["subjectTransactionId"]): list(record["acceptedClaims"])
                for record in accepted_records
            }
            judgment_ids = {
                str(record["subjectTransactionId"]): str(record["judgmentId"])
                for record in accepted_records
            }
            if accepted_claims_by_transaction:
                problem_ledger_head = manifest.get("problemLedgerHead")
                if not isinstance(problem_ledger_head, str):
                    raise MathFlowError(
                        "hierarchical research v5 history has no problem ledger head"
                    )
                replayed_state = apply_research_program_batch_delta_v5(
                    prior_state,
                    program_delta,
                    ledger_head=problem_ledger_head,
                    accepted_claims_by_transaction=accepted_claims_by_transaction,
                    judgment_ids=judgment_ids,
                )
                if replayed_state != post_state:
                    raise MathFlowError(
                        "hierarchical research v5 history delta does not reproduce its post state"
                    )
            elif program_delta != {
                "schemaVersion": 2,
                "operations": [],
                "contributions": [],
                "placementAudits": [],
            } or post_state != prior_state:
                raise MathFlowError(
                    "excluded-only hierarchical research v5 history must preserve its base state"
                )

        for program_id, program in post_state["programs"].items():
            if program_id == "root" or program_id in prior_state["programs"]:
                continue
            parent_id = program.get("parentId")
            if not isinstance(parent_id, str):
                raise MathFlowError("new research program has no credit parent")
            references[(parent_id, "program", str(program_id))] = (
                prior_state,
                post_state,
            )
        for transaction_id, contribution in post_state["contributions"].items():
            if transaction_id in prior_state["contributions"]:
                continue
            program_id = contribution.get("directProgramId")
            if not isinstance(program_id, str):
                raise MathFlowError("new research contribution has no direct program")
            references[(program_id, "contribution", str(transaction_id))] = (
                prior_state,
                post_state,
            )

        trace.append(
            {
                "runDigest": run_digest,
                "baseRunDigest": prior_digest,
                "baseProgramStateDigest": prior_state["stateDigest"],
                "postProgramStateDigest": post_state["stateDigest"],
                "acceptedRecords": accepted_records,
                "programDelta": program_delta,
            }
        )
        history_run_digests.append(run_digest)
        prior_state = post_state
        prior_digest = run_digest

    if prior_state.get("stateDigest") != latest_state.get("stateDigest"):
        raise MathFlowError("hierarchical research history does not reproduce the locked state")
    expected_transactions = set(str(key) for key in latest_state["contributions"])
    if accepted_transactions != expected_transactions:
        detail = sorted(expected_transactions ^ accepted_transactions)[0]
        raise MathFlowError(
            f"hierarchical credit history does not cover accepted contribution: {detail}"
        )
    expected_references = {
        (program_id, str(child["kind"]), str(child["id"]))
        for program_id in latest_state["programs"]
        for child in credit_children(latest_state, str(program_id))
    }
    if set(references) != expected_references:
        detail = sorted(expected_references ^ set(references))[0]
        raise MathFlowError(
            "hierarchical credit history has no unique first-appearance reference for "
            f"{detail[0]}/{detail[1]}/{detail[2]}"
        )
    return trace, history_run_digests, references


def _descendant_program_ids(
    state: dict[str, object], program_id: str
) -> set[str]:
    descendants = {program_id}
    frontier = [program_id]
    while frontier:
        parent = frontier.pop()
        for candidate_id, candidate in state["programs"].items():
            if candidate.get("parentId") == parent and candidate_id not in descendants:
                descendants.add(str(candidate_id))
                frontier.append(str(candidate_id))
    return descendants


def _local_threads(
    state: dict[str, object], program_id: str
) -> list[dict[str, object]]:
    return [
        thread
        for _, thread in sorted(state["threads"].items())
        if thread.get("programId") == program_id
    ]


def _evaluation_context(
    state: dict[str, object],
    targets: dict[str, list[dict[str, str]]],
    references: dict[
        tuple[str, str, str], tuple[dict[str, object], dict[str, object]]
    ],
) -> dict[str, object]:
    programs: list[dict[str, object]] = []
    for program_id, children in targets.items():
        child_contexts: list[dict[str, object]] = []
        for child in children:
            kind = str(child["kind"])
            child_id = str(child["id"])
            base_state, post_state = references[(program_id, kind, child_id)]
            if kind == "contribution":
                contribution = state["contributions"][child_id]
                child_state: dict[str, object] = {
                    "contribution": contribution,
                    "items": [
                        state["items"][item_id]
                        for item_id in contribution["itemIds"]
                    ],
                }
            else:
                descendants = _descendant_program_ids(state, child_id)
                child_state = {
                    "program": state["programs"][child_id],
                    "descendantProgramIds": sorted(descendants),
                    "currentThreads": [
                        thread
                        for thread in state["threads"].values()
                        if thread.get("programId") in descendants
                    ],
                    "currentItems": [
                        item
                        for item in state["items"].values()
                        if item.get("programId") in descendants
                    ],
                    "currentContributionIds": sorted(
                        transaction_id
                        for transaction_id, contribution in state[
                            "contributions"
                        ].items()
                        if contribution.get("directProgramId") in descendants
                    ),
                }
            child_contexts.append(
                {
                    "kind": kind,
                    "id": child_id,
                    "directThreadIds": credit_child_thread_ids(
                        state, program_id, kind, child_id
                    ),
                    "referenceBaseStateDigest": base_state["stateDigest"],
                    "referencePostStateDigest": post_state["stateDigest"],
                    "referenceBaseLocalThreads": _local_threads(
                        base_state, program_id
                    ),
                    "referencePostLocalThreads": _local_threads(
                        post_state, program_id
                    ),
                    "currentState": child_state,
                }
            )
        programs.append(
            {
                "program": state["programs"][program_id],
                "horizonLocalThreads": _local_threads(state, program_id),
                "children": child_contexts,
            }
        )
    return {
        "horizonStateDigest": state["stateDigest"],
        "horizonLedgerHead": state["ledgerHead"],
        "programs": programs,
    }


def _empty_credit_state(program_state: dict[str, object]) -> dict[str, object]:
    core = {
        "schemaVersion": 1,
        "problemId": program_state["problemId"],
        "programStateDigest": program_state["stateDigest"],
        "horizonStateDigest": program_state["stateDigest"],
        "baseCreditStateDigest": None,
        "evaluations": {},
        "allocations": {},
        "residualAllocations": {
            "root": {"numerator": "1", "denominator": "1"}
        },
    }
    state = {**core, "stateDigest": f"sha256:{sha256_json(core)}"}
    validate_credit_against_program_state(program_state, state)
    return state


def _allowed_credit_evidence_refs(
    program_state: dict[str, object],
    history: list[dict[str, object]],
) -> list[str]:
    allowed = {
        str(program_state["stateDigest"]),
        str(program_state["ledgerHead"]),
        *map(str, program_state["programs"]),
        *map(str, program_state["threads"]),
        *map(str, program_state["items"]),
        *map(str, program_state["contributions"]),
    }
    for entry in history:
        if not isinstance(entry, dict):
            continue
        for field in (
            "runDigest",
            "baseRunDigest",
            "baseProgramStateDigest",
            "postProgramStateDigest",
        ):
            value = entry.get(field)
            if isinstance(value, str):
                allowed.add(value)
        accepted_records = entry.get("acceptedRecords")
        if not isinstance(accepted_records, list):
            continue
        for record in accepted_records:
            if not isinstance(record, dict):
                continue
            for field in (
                "subjectTransactionId",
                "judgmentId",
                "judgmentRunDigest",
            ):
                value = record.get(field)
                if isinstance(value, str):
                    allowed.add(value)
    return sorted(allowed)


def _validate_credit_evidence_refs(
    credit_state: dict[str, object],
    program_state: dict[str, object],
    history: list[dict[str, object]],
) -> None:
    allowed = set(_allowed_credit_evidence_refs(program_state, history))
    for evaluation in credit_state["evaluations"].values():
        for child in evaluation["children"]:
            unknown = set(child["evidenceRefs"]) - allowed
            if unknown:
                raise MathFlowError(
                    "hierarchical credit cites evidence outside its locked context: "
                    f"{sorted(unknown)[0]}"
                )


def _normalized_credit_text_matches(raw: object, materialized: object) -> bool:
    return (
        isinstance(raw, str)
        and bool(raw.strip())
        and isinstance(materialized, str)
        and raw.strip() == materialized
    )


def _normalized_credit_decimal_matches(raw: object, materialized: object) -> bool:
    if (
        not isinstance(raw, str)
        or _CREDIT_WORK_TEXT.fullmatch(raw) is None
        or not isinstance(materialized, str)
    ):
        return False
    try:
        return Decimal(raw) == Decimal(materialized)
    except InvalidOperation:
        return False


def _normalized_credit_effects_match(
    raw: object,
    materialized: object,
) -> bool:
    if (
        not isinstance(raw, list)
        or not isinstance(materialized, list)
        or len(raw) != len(materialized)
    ):
        return False
    for raw_effect, materialized_effect in zip(raw, materialized, strict=True):
        if (
            not isinstance(raw_effect, dict)
            or set(raw_effect) != _CREDIT_EFFECT_FIELDS
            or not isinstance(materialized_effect, dict)
            or raw_effect.get("threadId") != materialized_effect.get("threadId")
            or not _normalized_credit_decimal_matches(
                raw_effect.get("withoutWork"),
                materialized_effect.get("withoutWork"),
            )
            or not _normalized_credit_decimal_matches(
                raw_effect.get("withWork"),
                materialized_effect.get("withWork"),
            )
            or not _normalized_credit_text_matches(
                raw_effect.get("rationale"),
                materialized_effect.get("rationale"),
            )
        ):
            return False
    return True


def load_hierarchical_credit_assignment_bundle(
    bundle_dir: Path,
) -> tuple[dict[str, object], dict[str, object], str]:
    manifest, run_digest = verify_bundle(bundle_dir)
    if (
        manifest.get("runKind") != "credit-assignment"
        or manifest.get("outputProfile") != HIERARCHICAL_CREDIT_PROFILE
        or not isinstance(manifest.get("problemId"), str)
    ):
        raise MathFlowError("bundle is not a hierarchical research credit assignment")
    try:
        dependency_lock = json.loads(
            read_verified_artifact(bundle_dir, manifest, "dependency-lock")
        )
        credit_input = json.loads(
            read_verified_artifact(bundle_dir, manifest, "hierarchical-credit-input")
        )
        history = json.loads(
            read_verified_artifact(bundle_dir, manifest, "research-history-trace")
        )
        context = json.loads(
            read_verified_artifact(bundle_dir, manifest, "hierarchical-credit-context")
        )
        program_state_bytes = read_verified_artifact(
            bundle_dir, manifest, "research-program-state"
        )
        program_state = json.loads(program_state_bytes)
        credit_delta = json.loads(
            read_verified_artifact(bundle_dir, manifest, "hierarchical-credit-delta")
        )
        credit_state = json.loads(
            read_verified_artifact(bundle_dir, manifest, "hierarchical-credit-state")
        )
        read_verified_artifact(
            bundle_dir, manifest, "accepted-submission-evidence"
        ).decode("utf-8")
    except json.JSONDecodeError as exc:
        raise MathFlowError("hierarchical credit bundle contains invalid JSON") from exc
    except UnicodeDecodeError as exc:
        raise MathFlowError("hierarchical credit evidence is not UTF-8") from exc
    problem = str(manifest["problemId"])
    validate_research_program_state(program_state, problem)
    validate_credit_against_program_state(program_state, credit_state)
    if not isinstance(credit_delta, dict) or set(credit_delta) != {
        "schemaVersion",
        "evaluations",
    }:
        raise MathFlowError("hierarchical credit bundle has an invalid raw delta")
    if not isinstance(history, list) or not isinstance(context, dict):
        raise MathFlowError("hierarchical credit bundle has invalid context artifacts")
    dependencies = (
        dependency_lock.get("dependencies")
        if isinstance(dependency_lock, dict)
        else None
    )
    projection_dependency_state_digest(dependency_lock)
    consumer = dependency_lock.get("consumer")
    locked_ledger = dependency_lock.get("problemLedger")
    research_dependencies = [
        item
        for item in dependencies
        if isinstance(item, dict)
        and item.get("artifactRole") == "research-program-state"
    ] if isinstance(dependencies, list) else []
    if len(research_dependencies) != 1:
        raise MathFlowError(
            "hierarchical credit bundle must lock one research-program state"
        )
    dependency = research_dependencies[0]
    artifact = dependency.get("artifact")
    manifest_inputs = manifest.get("inputs")
    required_input_fields = {
        "schemaVersion",
        "problemId",
        "projectionId",
        "projectionSpecDigest",
        "dependencyLockDigest",
        "researchRunDigest",
        "historyRunDigests",
        "programStateDigest",
        "horizonStateDigest",
        "acceptedTransactionIds",
        "schedule",
    }
    if not isinstance(credit_input, dict):
        raise MathFlowError("hierarchical credit input must be an object")
    schedule = validate_credit_run_schedule(credit_input.get("schedule"))
    if schedule.get("mode") != "rolling":
        raise MathFlowError(
            "hierarchical research credit requires a rolling common-horizon schedule"
        )
    accepted_trace_ids = sorted(
        str(record["subjectTransactionId"])
        for entry in history
        if isinstance(entry, dict)
        for record in entry.get("acceptedRecords", [])
        if isinstance(record, dict)
        and isinstance(record.get("subjectTransactionId"), str)
    )
    raw_evaluations = {
        str(evaluation.get("programId")): evaluation
        for evaluation in credit_delta.get("evaluations", [])
        if isinstance(evaluation, dict)
        and isinstance(evaluation.get("programId"), str)
    }
    materialized_evaluations = credit_state.get("evaluations")
    if not isinstance(materialized_evaluations, dict) or set(raw_evaluations) != set(
        materialized_evaluations
    ):
        raise MathFlowError(
            "hierarchical credit raw delta does not match its materialized programs"
        )
    for program_id, raw_evaluation in raw_evaluations.items():
        materialized = materialized_evaluations[program_id]
        raw_children = raw_evaluation.get("children")
        materialized_children = materialized.get("children")
        if (
            not isinstance(raw_children, list)
            or not isinstance(materialized_children, list)
            or set(raw_evaluation)
            != {"programId", "unattributedWork", "rationale", "children"}
            or not _normalized_credit_decimal_matches(
                raw_evaluation.get("unattributedWork"),
                materialized.get("unattributedWork"),
            )
            or not _normalized_credit_text_matches(
                raw_evaluation.get("rationale"),
                materialized.get("rationale"),
            )
            or len(raw_children) != len(materialized_children)
        ):
            raise MathFlowError(
                "hierarchical credit raw delta does not match its materialized state"
            )
        raw_by_child = {
            (str(child.get("kind")), str(child.get("id"))): child
            for child in raw_children
            if isinstance(child, dict)
        }
        materialized_by_child = {
            (str(child.get("kind")), str(child.get("id"))): child
            for child in materialized_children
            if isinstance(child, dict)
        }
        if set(raw_by_child) != set(materialized_by_child):
            raise MathFlowError(
                "hierarchical credit raw delta does not match its materialized children"
            )
        for child_key, raw_child in raw_by_child.items():
            materialized_child = materialized_by_child[child_key]
            if (
                set(raw_child) != _CREDIT_CHILD_FIELDS
                or not _normalized_credit_text_matches(
                    raw_child.get("counterfactual"),
                    materialized_child.get("counterfactual"),
                )
                or not _normalized_credit_effects_match(
                    raw_child.get("directEffects"),
                    materialized_child.get("directEffects"),
                )
                or not _normalized_credit_effects_match(
                    raw_child.get("obviatedEffects"),
                    materialized_child.get("obviatedEffects"),
                )
                or raw_child.get("confidence")
                != materialized_child.get("confidence")
                or raw_child.get("evidenceRefs")
                != materialized_child.get("evidenceRefs")
            ):
                raise MathFlowError(
                    "hierarchical credit raw child differs from its materialized state"
                )
    if (
        set(credit_input) != required_input_fields
        or credit_input.get("schemaVersion") != 1
        or credit_input.get("problemId") != problem
        or credit_input.get("programStateDigest") != program_state.get("stateDigest")
        or credit_input.get("horizonStateDigest") != program_state.get("stateDigest")
        or credit_state.get("programStateDigest") != program_state.get("stateDigest")
        or credit_state.get("horizonStateDigest") != program_state.get("stateDigest")
        or credit_state.get("baseCreditStateDigest") is not None
        or not isinstance(artifact, dict)
        or artifact.get("digest") != sha256_bytes(program_state_bytes)
        or credit_input.get("researchRunDigest") != dependency.get("runDigest")
        or credit_input.get("dependencyLockDigest")
        != dependency_lock.get("dependencyLockDigest")
        or not isinstance(consumer, dict)
        or consumer.get("projectionId") != credit_input.get("projectionId")
        or consumer.get("projectionSpecDigest")
        != credit_input.get("projectionSpecDigest")
        or consumer.get("problemId") != problem
        or consumer.get("canonicalHead") != manifest.get("ledgerHead")
        or not isinstance(locked_ledger, dict)
        or locked_ledger.get("problemLedgerHead")
        != manifest.get("problemLedgerHead")
        or locked_ledger.get("problemLedgerDigest")
        != manifest.get("problemLedgerDigest")
        or not isinstance(manifest_inputs, dict)
        or manifest_inputs.get("projectionId") != credit_input.get("projectionId")
        or manifest_inputs.get("projectionSpecDigest")
        != credit_input.get("projectionSpecDigest")
        or manifest_inputs.get("dependencyLockDigest")
        != credit_input.get("dependencyLockDigest")
        or manifest_inputs.get("dependencyRunDigests")
        != [dependency.get("runDigest")]
        or manifest_inputs.get("schedule") != schedule
        or credit_input.get("schedule") != schedule
        or credit_input.get("historyRunDigests")
        != [entry.get("runDigest") for entry in history]
        or not credit_input.get("historyRunDigests")
        or credit_input["historyRunDigests"][-1]
        != credit_input.get("researchRunDigest")
        or credit_input.get("acceptedTransactionIds")
        != sorted(str(key) for key in program_state["contributions"])
        or accepted_trace_ids != credit_input.get("acceptedTransactionIds")
        or context.get("horizonStateDigest") != program_state.get("stateDigest")
    ):
        raise MathFlowError("hierarchical credit bundle inputs are inconsistent")
    validate_hierarchical_credit_state(credit_state, problem)
    _validate_credit_evidence_refs(credit_state, program_state, history)
    return manifest, credit_state, run_digest


def run_hierarchical_credit_assignment_bundle(
    root: Path,
    projection_root: Path,
    projection: str,
    problem: str,
    head: str,
    output_dir: Path,
    transport: OpenRouterTransport | None = None,
    *,
    as_of: int | None = None,
) -> dict[str, object]:
    root = root.resolve()
    projection_root = projection_root.resolve()
    resolved = resolve_projection(root, projection, problem, head)
    runner = resolved.get("runner")
    if (
        resolved.get("engine") != "overlay-repository-v1"
        or not isinstance(runner, dict)
        or runner.get("implementation")
        != "openrouter-hierarchical-research-credit-v2"
        or not isinstance(runner.get("spec"), str)
    ):
        raise MathFlowError(
            "credit projection does not select hierarchical research credit v2"
        )
    spec = load_judge_spec(root / str(runner["spec"]))
    canonical_spec = json.loads(
        read_at(root, str(resolved["canonicalHead"]), str(runner["spec"]))
    )
    if spec != canonical_spec or spec.get("implementation") != runner.get(
        "implementation"
    ):
        raise MathFlowError(
            "hierarchical credit judge spec differs from the canonical projection head"
        )
    credit_policy = _credit_policy(root, spec)
    plan = plan_credit_run(
        root, projection_root, projection, problem, head, as_of
    )
    if plan.get("eligible") is not True:
        raise MathFlowError(
            "credit run is not eligible: "
            f"{plan.get('reasonCode')}: {plan.get('message')}"
        )
    schedule = validate_credit_run_schedule(plan.get("schedule"))
    if schedule.get("mode") != "rolling":
        raise MathFlowError(
            "hierarchical research credit requires a rolling common-horizon schedule"
        )
    dependency_lock = resolve_projection_dependencies(
        root, projection_root, projection, problem, head
    )
    if dependency_lock.get("dependencyLockDigest") != plan.get(
        "dependencyLockDigest"
    ):
        raise MathFlowError(
            "hierarchical credit dependency changed after eligibility planning"
        )
    research_dependencies = [
        item
        for item in dependency_lock["dependencies"]
        if item.get("artifactRole") == "research-program-state"
    ]
    if len(research_dependencies) != 1:
        raise MathFlowError(
            "hierarchical credit requires exactly one research-program-state dependency"
        )
    dependency = research_dependencies[0]
    research_bundle, _, program_state, research_run_digest = _locked_research_state(
        projection_root, dependency, problem
    )
    source = load_source(root, problem, head)
    if source["problemLedgerDigest"] != dependency_lock["problemLedger"][
        "problemLedgerDigest"
    ]:
        raise MathFlowError(
            "hierarchical credit source ledger does not match its dependency lock"
        )

    trace, history_run_digests, references = _accepted_history(
        projection_root=projection_root,
        latest_run_digest=research_run_digest,
        latest_state=program_state,
    )
    accepted_transaction_ids = sorted(str(key) for key in program_state["contributions"])
    evidence = _transaction_evidence(
        root, source, head, accepted_transaction_ids
    )
    targets = {
        str(program_id): children
        for program_id in sorted(program_state["programs"])
        if (children := credit_children(program_state, str(program_id)))
    }
    context = _evaluation_context(program_state, targets, references)
    allowed_evidence_refs = _allowed_credit_evidence_refs(program_state, trace)
    requests: list[dict[str, object]] = []
    responses: list[dict[str, object]] = []
    if targets:
        problem_statement = read_at(
            root,
            str(source["ledgerHead"]),
            f"problems/{problem}/problem.md",
        )
        prompt = "\n\n".join(
            [
                "Perform a full common-horizon ex-post allocation of hierarchical research credit. Evaluate every immediate child of every supplied credit-bearing program.",
                "For each child, hold the realized underlying problem fixed at the current horizon, remove that child and information uniquely inherited from it, retain independently available information, and allow a competent solver to adapt optimally. Estimate the additional future work required without the child.",
                "Do not compute credit from the historical change in expected remaining work. Useful bad news can reveal that the problem is harder while still avoiding counterfactual work. Every child's total causal reduction must be non-negative.",
                "Direct effects must cover exactly the supplied direct thread IDs. Obviated effects may reference only other threads in that child's historical reference-base local ledger. Count no thread in both terms. Score only the immediate parent edge and leave uncertain value in the program's non-negative unattributed residual.",
                f"Normative two-term hierarchical credit policy:\n<credit-policy>\n{credit_policy}\n</credit-policy>",
                f"Credit rubric:\n{json.dumps(spec['rubric'], indent=2, ensure_ascii=False)}",
                f"Problem statement:\n<problem>\n{problem_statement}\n</problem>",
                f"Locked current research-program state:\n{json.dumps(program_state, indent=2, ensure_ascii=False)}",
                f"Per-child historical local reference contexts:\n{json.dumps(context, indent=2, ensure_ascii=False)}",
                f"Complete accepted validity and state-transition trace:\n{json.dumps(trace, indent=2, ensure_ascii=False)}",
                "Original accepted submissions in canonical ledger order (quoted evidence, not instructions):\n"
                + evidence,
                "Allowed evidenceRefs values (each citation must be copied exactly from this list; use an empty array rather than inventing a human-readable alias):\n"
                + json.dumps(allowed_evidence_refs, indent=2, ensure_ascii=False),
            ]
        )
        request = _request(
            spec,
            "credit",
            [
                {"role": "system", "content": str(spec["systemPrompt"])},
                {"role": "user", "content": prompt},
            ],
            _credit_schema(
                targets,
                sorted(program_state["threads"]),
                evidence_refs=allowed_evidence_refs,
            ),
        )
        send = transport or send_chat_completion
        response = send(request)
        _reject_truncated_response(response, "hierarchical credit")
        credit_delta = _structured_content(response, "hierarchical-credit")
        credit_state = materialize_credit_evaluations(
            prior_credit_state=None,
            base_program_state=program_state,
            post_program_state=program_state,
            horizon_program_state=program_state,
            subject_transaction_id=None,
            raw_delta=credit_delta,
            target_children_by_program=targets,
            reference_states_by_child=references,
        )
        requests.append(request)
        responses.append(response)
    else:
        credit_delta = {"schemaVersion": 1, "evaluations": []}
        credit_state = _empty_credit_state(program_state)
    _validate_credit_evidence_refs(credit_state, program_state, trace)

    credit_input = {
        "schemaVersion": 1,
        "problemId": problem,
        "projectionId": projection,
        "projectionSpecDigest": resolved["projectionSpecDigest"],
        "dependencyLockDigest": dependency_lock["dependencyLockDigest"],
        "researchRunDigest": research_run_digest,
        "historyRunDigests": history_run_digests,
        "programStateDigest": program_state["stateDigest"],
        "horizonStateDigest": program_state["stateDigest"],
        "acceptedTransactionIds": accepted_transaction_ids,
        "schedule": schedule,
    }
    bundle = ArtifactBundle(output_dir)
    bundle.add_json(
        "control/dependencies.json", dependency_lock, "dependency-lock"
    )
    bundle.add_json(
        "control/input.json", credit_input, "hierarchical-credit-input"
    )
    bundle.add_json(
        "input/history.json", trace, "research-history-trace"
    )
    bundle.add_json(
        "input/context.json", context, "hierarchical-credit-context"
    )
    bundle.add_text(
        "input/submissions.md",
        evidence,
        "accepted-submission-evidence",
        "text/markdown",
    )
    state_bytes = read_verified_artifact(
        research_bundle,
        verify_bundle(research_bundle)[0],
        "research-program-state",
    )
    bundle.add_bytes(
        "state/research.json",
        state_bytes,
        "research-program-state",
        "application/json",
    )
    bundle.add_json(
        "credit/delta.json", credit_delta, "hierarchical-credit-delta"
    )
    bundle.add_json(
        "credit/state.json", credit_state, "hierarchical-credit-state"
    )
    envelope = run_envelope(
        problem,
        source,
        spec,
        None,
        [f"sha256:{sha256_json(request)}" for request in requests],
        [
            _provider_run(response, str(request["model"]), "credit")
            for request, response in zip(requests, responses, strict=True)
        ],
        run_kind="credit-assignment",
        inputs={
            "projectionId": projection,
            "projectionSpecDigest": resolved["projectionSpecDigest"],
            "dependencyLockDigest": dependency_lock["dependencyLockDigest"],
            "dependencyRunDigests": [research_run_digest],
            "schedule": schedule,
        },
    )
    manifest = bundle.finalize(envelope)
    load_hierarchical_credit_assignment_bundle(output_dir)
    return manifest
