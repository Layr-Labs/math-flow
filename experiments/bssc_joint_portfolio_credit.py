"""Complete the successful BSSC joint K2 W+ result with W- and credit."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path

from experiments.bssc_accounting_topology_holdout import (
    PROBLEM_ID,
    _accepted_entry_by_ordinal,
    response_summaries,
)
from experiments.bssc_accounting_topology_prompt import (
    load_json,
    materialize_case,
    state_summary,
    write_json,
)
from experiments.bssc_joint_portfolio_wplus import _bound_file, _candidate_spec
from experiments.bssc_local_builder_v10 import (
    BudgetedCapturingTransport,
    _scenario_artifact,
    _serialized_measurement,
    _usage_totals,
)
from math_flow.bssc_research_v4_producer import _accepted_frontier
from math_flow.errors import MathFlowError
from math_flow.governed_providers import OpenRouterWorkProjectionProviderV2
from math_flow.joint_portfolio_credit_experiment import (
    run_joint_portfolio_credit_candidate,
)
from math_flow.joint_portfolio_wplus_experiment import (
    reduce_joint_portfolio_wplus_response_v3,
    validate_fixed_semantic_packet,
)
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.repository import sha256_json
from math_flow.teacher_student_scenarios import _score_json_relational
from math_flow.work_accounting import (
    validate_root_contract,
    validate_work_accounting_state,
)


def _object_digest(value: object) -> str:
    return f"sha256:{sha256_json(copy.deepcopy(value))}"


def _load_source_inputs(
    root: Path,
    output: Path,
    manifest: dict[str, object],
) -> dict[str, object]:
    source_manifest_path = _bound_file(
        root,
        manifest["sourceExperimentManifest"],
        manifest["sourceExperimentManifestFileDigest"],
    )
    source = load_json(source_manifest_path)
    if not isinstance(source, dict) or source.get("id") != manifest.get(
        "sourceExperimentId"
    ):
        raise MathFlowError("joint credit source experiment is invalid")
    if source.get("status") != "unpublished-experiment" or not source.get(
        "publicationForbidden"
    ):
        raise MathFlowError("joint credit source must remain unpublished")
    response_path = _bound_file(
        root,
        manifest["frozenJointResponse"],
        manifest["frozenJointResponseFileDigest"],
    )
    response = load_json(response_path)
    if _object_digest(response) != manifest.get("frozenJointResponseDigest"):
        raise MathFlowError("joint credit frozen response content binding mismatch")
    base_path = _bound_file(
        root, source["fixedBase"]["fixture"], source["fixedBase"]["fileDigest"]
    )
    base = validate_research_program_state_v3(load_json(base_path), PROBLEM_ID)
    if base["stateDigest"] != source["fixedBase"]["stateDigest"]:
        raise MathFlowError("joint credit fixed knowledge base binding mismatch")
    contract_path = _bound_file(
        root, source["rootContract"], source["rootContractFileDigest"]
    )
    contract = validate_root_contract(load_json(contract_path), PROBLEM_ID)
    if contract["rootContractDigest"] != source["rootContractDigest"]:
        raise MathFlowError("joint credit root contract binding mismatch")
    accounting_path = _bound_file(
        root,
        source["fixedBaseAccounting"]["fixture"],
        source["fixedBaseAccounting"]["fileDigest"],
    )
    accounting = validate_work_accounting_state(
        load_json(accounting_path), base, contract
    )
    if accounting["stateDigest"] != source["fixedBaseAccounting"]["stateDigest"]:
        raise MathFlowError("joint credit fixed accounting base binding mismatch")
    semantic_path = _bound_file(
        root, source["fixedSemanticPacket"], source["fixedSemanticPacketDigest"]
    )
    semantic = validate_fixed_semantic_packet(
        load_json(semantic_path),
        problem_id=PROBLEM_ID,
        base_state_digest=str(base["stateDigest"]),
        external_dependency_result_ids=set(base["intermediateResults"]),
    )
    if semantic["packetDigest"] != source["semanticPacketDigest"]:
        raise MathFlowError("joint credit semantic packet binding mismatch")
    relational_path = _bound_file(
        root, source["relationalGold"], source["relationalGoldDigest"]
    )
    relational = load_json(relational_path)
    if not isinstance(relational, dict):
        raise MathFlowError("joint credit relational gate is invalid")

    validity_source = load_json(
        root / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
    )
    if not isinstance(validity_source, dict):
        raise MathFlowError("joint credit validity source is invalid")
    pins, accepted = _accepted_frontier(root, validity_source)
    ordinal = int(manifest["acceptedTransitionOrdinal"])
    case = materialize_case(
        root,
        projection_commit=str(pins["projectionCommit"]),
        entry=_accepted_entry_by_ordinal(accepted, ordinal),
        directory=output / "inputs" / f"k{ordinal}",
    )
    if case["subject"] != semantic["subjectTransactionId"]:
        raise MathFlowError("joint credit source and canonical case disagree")
    reduced = reduce_joint_portfolio_wplus_response_v3(
        response,
        base_state=base,
        base_accounting_state=accounting,
        root_contract=contract,
        semantic_packet=semantic,
        accepted_claims=case["claims"],
        judgment_id=str(case["judgmentId"]),
        evidence_files=case["evidenceFiles"],
    )
    topology = state_summary(reduced["postState"], str(case["subject"]))
    score = _score_json_relational(
        relational,
        {
            "fixed-base-state": _scenario_artifact(base),
            f"k{ordinal}.author.transition": _scenario_artifact(
                reduced["transition"]
            ),
            f"k{ordinal}.author.topology": _scenario_artifact(topology),
        },
        variant="joint-portfolio-wplus-v3",
        seed=int(manifest["seed"]),
        scorer_id=str(manifest["id"]),
    )
    if score.get("status") != "passed":
        raise MathFlowError("joint credit frozen W+ response no longer passes its gate")
    expected = manifest.get("frozenJointOutcome")
    if not isinstance(expected, dict) or any(
        actual != expected.get(field)
        for field, actual in {
            "postStateDigest": reduced["postState"]["stateDigest"],
            "withAccessStateDigest": reduced["withAccessState"]["stateDigest"],
            "withAccessWorkHours": reduced["withAccessState"]["totalWorkHours"],
        }.items()
    ):
        raise MathFlowError("joint credit frozen W+ outcome binding mismatch")
    return {
        "sourceManifest": source,
        "response": response,
        "base": base,
        "accounting": accounting,
        "contract": contract,
        "semantic": semantic,
        "case": case,
        "reduced": reduced,
        "topology": topology,
        "score": score,
        "pins": pins,
    }


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise MathFlowError("joint credit experiment output must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(root)
    except ValueError as exc:
        raise MathFlowError("joint credit manifest escapes the repository") from exc
    manifest = load_json(manifest_path)
    if (
        not isinstance(manifest, dict)
        or manifest.get("problemId") != PROBLEM_ID
        or manifest.get("status") != "unpublished-experiment"
        or not manifest.get("publicationForbidden")
    ):
        raise MathFlowError("joint credit experiment manifest is invalid")
    inputs = _load_source_inputs(root, output, manifest)
    for name, value in inputs["reduced"].items():
        write_json(output / "joint" / f"{name}.json", value)
    write_json(output / "joint" / "topology-summary.json", inputs["topology"])
    write_json(output / "joint" / "relational-score.json", inputs["score"])
    plan = {
        "schemaVersion": 1,
        "experiment": manifest,
        "dryRun": args.dry_run,
        "mainCommit": inputs["pins"]["mainCommit"],
        "projectionCommit": inputs["pins"]["projectionCommit"],
        "subjectTransactionId": inputs["case"]["subject"],
        "frozenWithAccessStateDigest": inputs["reduced"]["withAccessState"][
            "stateDigest"
        ],
        "plannedProviderCalls": 0
        if args.dry_run
        else manifest["maximumProviderCalls"],
    }
    write_json(output / "plan.json", plan)
    if args.dry_run:
        write_json(
            output / "complete.json",
            {
                **plan,
                "status": "dry-run",
                "providerCalls": 0,
                "jointPrerequisiteVerified": True,
            },
        )
        return 0

    judge_path = _bound_file(
        root, manifest["workJudgeSpec"], manifest["workJudgeSpecFileDigest"]
    )
    base_spec = load_json(judge_path)
    if (
        not isinstance(base_spec, dict)
        or base_spec.get("implementation") != "openrouter-work-accounting-v2"
        or base_spec.get("model") != manifest.get("model")
    ):
        raise MathFlowError("joint credit work judge binding mismatch")
    spec = _candidate_spec(
        base_spec,
        seed=int(manifest["seed"]),
        maximum_attempts=int(manifest["maximumAttempts"]),
    )
    write_json(output / "work-judge-spec.json", spec)
    transport = BudgetedCapturingTransport(
        maximum_calls=int(manifest["maximumProviderCalls"]),
        maximum_cost_usd=float(manifest["maximumReportedCostUsd"]),
        maximum_single_call_cost_usd=float(manifest["maximumSingleCallCostUsd"]),
        maximum_request_bytes=int(manifest["maximumRequestBytes"]),
        maximum_total_tokens=int(manifest["maximumTotalProviderTokens"]),
    )
    provider = OpenRouterWorkProjectionProviderV2(spec, transport=transport)
    status = "completed"
    error: dict[str, object] | None = None
    try:
        result = run_joint_portfolio_credit_candidate(
            provider=provider,
            subject_transaction_id=str(inputs["case"]["subject"]),
            root_contract=inputs["contract"],
            base_knowledge_state=inputs["base"],
            base_accounting_state=inputs["accounting"],
            joint_response=inputs["response"],
            semantic_packet=inputs["semantic"],
            accepted_claims=inputs["case"]["claims"],
            accepted_claim_refs=inputs["case"]["acceptedClaimRefs"],
            judgment_id=str(inputs["case"]["judgmentId"]),
            evidence_manifest=inputs["case"]["evidenceManifest"],
            evidence_chunks=inputs["case"]["evidenceChunks"],
            checkpoint_dir=output / "checkpoints",
            descendant_depth=int(manifest["descendantDepth"]),
        )
        for name, value in result.items():
            if name == "jointArtifacts":
                continue
            write_json(output / "credit" / f"{name}.json", value)
    except Exception as exc:  # noqa: BLE001 - preserve exact experiment failure
        status = "failed"
        error = {"errorType": type(exc).__name__, "error": str(exc)}
    write_json(output / "provider-requests.json", transport.requests)
    write_json(output / "provider-responses.json", transport.responses)
    completion = {
        **plan,
        "status": status,
        "providerCalls": len(transport.requests),
        "invocations": provider.invocation_records,
        "responses": response_summaries(transport),
        "usage": _usage_totals(transport.responses),
        "contextTelemetry": {
            "baseKnowledgeState": _serialized_measurement(inputs["base"]),
            "baseLiveWorkState": _serialized_measurement(inputs["accounting"]),
            "frozenPostKnowledgeState": _serialized_measurement(
                inputs["reduced"]["postState"]
            ),
            "frozenWithAccessState": _serialized_measurement(
                inputs["reduced"]["withAccessState"]
            ),
            "submissionEvidenceBytes": inputs["case"]["evidenceManifest"][
                "totalBytes"
            ],
            "submissionEvidenceFileCount": len(
                inputs["case"]["evidenceManifest"]["files"]
            ),
        },
        **({"failure": error} if error is not None else {}),
    }
    write_json(output / "complete.json", completion)
    return 0 if status == "completed" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(
            "protocol/experiments/bssc-joint-portfolio-credit-k2-v1/manifest.json"
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY") and "--dry-run" not in sys.argv:
        raise SystemExit("OPENROUTER_API_KEY is required unless --dry-run is used")
    raise SystemExit(run(parse_args(sys.argv[1:])))
