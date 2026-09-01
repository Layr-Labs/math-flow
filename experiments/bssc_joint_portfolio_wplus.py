"""Run the unpublished fixed-semantics BSSC joint topology/W+ K1 gate."""

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
from experiments.bssc_local_builder_v10 import (
    BudgetedCapturingTransport,
    _scenario_artifact,
    _serialized_measurement,
    _usage_totals,
)
from math_flow.artifacts import sha256_bytes
from math_flow.bssc_research_v4_producer import _accepted_frontier
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_wplus_experiment import (
    IMPLEMENTATION,
    IMPLEMENTATION_V2,
    OpenRouterJointPortfolioWPlusExperimentProvider,
    OpenRouterJointPortfolioWPlusExperimentProviderV2,
    validate_fixed_semantic_packet,
)
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.teacher_student_scenarios import _score_json_relational
from math_flow.work_accounting import validate_root_contract


def _bound_file(root: Path, relative: object, expected_digest: object) -> Path:
    path = (root / str(relative)).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise MathFlowError("joint topology/W+ experiment path escapes the repository") from exc
    if sha256_bytes(path.read_bytes()) != expected_digest:
        raise MathFlowError(f"joint topology/W+ experiment digest mismatch: {relative}")
    return path


def _candidate_spec(
    base: dict[str, object], *, seed: int, maximum_attempts: int
) -> dict[str, object]:
    spec = copy.deepcopy(base)
    parameters = dict(spec["parameters"])
    parameters["seed"] = seed
    spec["parameters"] = parameters
    retry = dict(spec["retryPolicy"])
    retry["maximumAttempts"] = maximum_attempts
    spec["retryPolicy"] = retry
    return spec


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise MathFlowError("joint topology/W+ experiment output must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(root)
    except ValueError as exc:
        raise MathFlowError("joint topology/W+ manifest escapes the repository") from exc
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get("problemId") != PROBLEM_ID:
        raise MathFlowError("joint topology/W+ manifest is invalid")
    if manifest.get("status") != "unpublished-experiment" or not manifest.get(
        "publicationForbidden"
    ):
        raise MathFlowError("joint topology/W+ experiment must forbid publication")

    judge_path = _bound_file(
        root, manifest["judgeSpec"], manifest["judgeSpecDigest"]
    )
    semantic_path = _bound_file(
        root, manifest["fixedSemanticPacket"], manifest["fixedSemanticPacketDigest"]
    )
    contract_path = _bound_file(
        root, manifest["rootContract"], manifest["rootContractFileDigest"]
    )
    relational_path = _bound_file(
        root, manifest["relationalGold"], manifest["relationalGoldDigest"]
    )
    fixed = manifest.get("fixedBase")
    if not isinstance(fixed, dict):
        raise MathFlowError("joint topology/W+ fixed base is invalid")
    fixed_path = _bound_file(root, fixed["fixture"], fixed["fileDigest"])
    fixed_base = validate_research_program_state_v3(load_json(fixed_path), PROBLEM_ID)
    if (
        fixed_base["stateDigest"] != fixed.get("stateDigest")
        or fixed_base["ledgerHead"] != fixed.get("ledgerHead")
    ):
        raise MathFlowError("joint topology/W+ fixed base binding mismatch")
    semantic_packet = validate_fixed_semantic_packet(
        load_json(semantic_path),
        problem_id=PROBLEM_ID,
        base_state_digest=str(fixed_base["stateDigest"]),
    )
    if semantic_packet["packetDigest"] != manifest.get("semanticPacketDigest"):
        raise MathFlowError("joint topology/W+ semantic packet content binding mismatch")
    root_contract = validate_root_contract(load_json(contract_path), PROBLEM_ID)
    if root_contract["rootContractDigest"] != manifest.get("rootContractDigest"):
        raise MathFlowError("joint topology/W+ root contract binding mismatch")
    base_spec = load_json(judge_path)
    relational_gold = load_json(relational_path)
    if not isinstance(base_spec, dict) or not isinstance(relational_gold, dict):
        raise MathFlowError("joint topology/W+ judge or gold is invalid")
    implementation = base_spec.get("implementation")
    if implementation == IMPLEMENTATION:
        provider_class = OpenRouterJointPortfolioWPlusExperimentProvider
        scorer_variant = "joint-portfolio-wplus-v1"
    elif implementation == IMPLEMENTATION_V2:
        provider_class = OpenRouterJointPortfolioWPlusExperimentProviderV2
        scorer_variant = "joint-portfolio-wplus-v2"
    else:
        raise MathFlowError("joint topology/W+ implementation is unsupported")
    if base_spec.get("model") != manifest.get("model"):
        raise MathFlowError("joint topology/W+ model binding mismatch")
    stage = base_spec.get("stages", {}).get("joint-portfolio-wplus", {})
    if (
        not isinstance(stage, dict)
        or stage.get("parameters", {}).get("reasoning", {}).get("effort")
        != manifest.get("reasoningEffort")
    ):
        raise MathFlowError("joint topology/W+ reasoning-effort binding mismatch")

    source = load_json(root / "protocol/runtime/bssc-research-v4-validity-source-v1.json")
    if not isinstance(source, dict):
        raise MathFlowError("joint topology/W+ validity source is invalid")
    pins, accepted = _accepted_frontier(root, source)
    ordinal = int(manifest["acceptedTransitionOrdinal"])
    case = materialize_case(
        root,
        projection_commit=str(pins["projectionCommit"]),
        entry=_accepted_entry_by_ordinal(accepted, ordinal),
        directory=output / "inputs" / f"k{ordinal}",
    )
    if case["subject"] != semantic_packet["subjectTransactionId"]:
        raise MathFlowError("joint topology/W+ fixed semantics names another canonical case")
    write_json(output / "fixed-base-state.json", fixed_base)

    seeds = tuple(int(value) for value in manifest.get("seeds", []))
    if args.seeds is not None:
        requested = tuple(int(value) for value in args.seeds.split(","))
        if not requested or not set(requested) <= set(seeds):
            raise MathFlowError("joint topology/W+ requested seed is outside the manifest")
        seeds = requested
    if not seeds or len(seeds) != len(set(seeds)):
        raise MathFlowError("joint topology/W+ seeds are invalid")

    maximum_attempts = int(manifest["maximumAttempts"])
    maximum_calls = int(manifest["maximumProviderCalls"])
    maximum_cost = float(manifest["maximumReportedCostUsd"])
    maximum_single_cost = float(manifest["maximumSingleCallCostUsd"])
    maximum_request_bytes = int(manifest["maximumRequestBytes"])
    maximum_total_tokens = int(manifest["maximumTotalProviderTokens"])
    plan = {
        "schemaVersion": 1,
        "experiment": manifest,
        "dryRun": args.dry_run,
        "mainCommit": pins["mainCommit"],
        "projectionCommit": pins["projectionCommit"],
        "seeds": list(seeds),
        "subjectTransactionId": case["subject"],
        "plannedProviderCalls": 0 if args.dry_run else maximum_calls,
    }
    write_json(output / "plan.json", plan)
    transport = BudgetedCapturingTransport(
        maximum_calls=maximum_calls,
        maximum_cost_usd=maximum_cost,
        maximum_single_call_cost_usd=maximum_single_cost,
        maximum_request_bytes=maximum_request_bytes,
        maximum_total_tokens=maximum_total_tokens,
    )
    chains: list[dict[str, object]] = []
    for seed in seeds:
        chain_dir = output / "chains" / f"seed-{seed}"
        spec = _candidate_spec(
            base_spec, seed=seed, maximum_attempts=maximum_attempts
        )
        write_json(chain_dir / "judge-spec.json", spec)
        chain: dict[str, object] = {
            "seed": seed,
            "status": "dry-run" if args.dry_run else "running",
            "subjectTransactionId": case["subject"],
            "baseStateDigest": fixed_base["stateDigest"],
        }
        if args.dry_run:
            write_json(chain_dir / "summary.json", chain)
            chains.append(chain)
            continue
        request_start = len(transport.requests)
        response_start = len(transport.responses)
        journals: list[dict[str, object]] = []
        provider = provider_class(
            spec,
            transport=transport,
            attempt_journal_writer=lambda value: journals.append(value),
        )
        try:
            artifacts = provider.run(
                problem_id=PROBLEM_ID,
                subject_transaction_id=str(case["subject"]),
                base_state=fixed_base,
                root_contract=root_contract,
                semantic_packet=semantic_packet,
                accepted_claims=case["claims"],
                judgment_id=str(case["judgmentId"]),
                evidence_files=case["evidenceFiles"],
            )
            for name, value in artifacts.items():
                write_json(chain_dir / f"{name}.json", value)
            topology = state_summary(artifacts["postState"], str(case["subject"]))
            write_json(chain_dir / "topology-summary.json", topology)
            score = _score_json_relational(
                relational_gold,
                {
                    "fixed-base-state": _scenario_artifact(fixed_base),
                    "k1.author.transition": _scenario_artifact(artifacts["transition"]),
                    "k1.author.topology": _scenario_artifact(topology),
                },
                variant=scorer_variant,
                seed=seed,
                scorer_id=str(manifest["id"]),
            )
            write_json(chain_dir / "relational-score.json", score)
            chain.update(
                {
                    "status": "completed" if score.get("status") == "passed" else "evaluation-failed",
                    "relationalScore": score,
                    "postStateDigest": artifacts["postState"]["stateDigest"],
                    "withAccessStateDigest": artifacts["withAccessState"]["stateDigest"],
                    "withAccessWorkHours": artifacts["withAccessState"]["totalWorkHours"],
                    "invocations": provider.invocation_records,
                    "contextTelemetry": {
                        "fixedSemanticPacket": _serialized_measurement(semantic_packet),
                        "acceptedClaimAssessments": _serialized_measurement(case["claims"]),
                        "baseKnowledgeState": _serialized_measurement(fixed_base),
                        "submissionEvidenceBytes": sum(
                            len(item.content) for item in case["evidenceFiles"]
                        ),
                        "submissionEvidenceFileCount": len(case["evidenceFiles"]),
                    },
                }
            )
        except Exception as exc:  # noqa: BLE001 - preserve experiment failure
            chain.update(
                {
                    "status": "failed",
                    "errorType": type(exc).__name__,
                    "error": str(exc),
                }
            )
        requests = transport.requests[request_start:]
        responses = transport.responses[response_start:]
        write_json(chain_dir / "provider-requests.json", requests)
        write_json(chain_dir / "provider-responses.json", responses)
        write_json(chain_dir / "attempt-journals.json", journals)
        chain["providerCalls"] = len(requests)
        chain["responses"] = response_summaries(
            type("Captured", (), {"requests": requests, "responses": responses})()
        )
        chain["usage"] = _usage_totals(responses)
        write_json(chain_dir / "summary.json", chain)
        chains.append(chain)

    completed = all(
        chain["status"] in {"completed", "dry-run"} for chain in chains
    )
    complete = {
        **plan,
        "status": "completed" if completed else "failed",
        "providerCalls": len(transport.requests),
        "usage": _usage_totals(transport.responses),
        "chains": chains,
    }
    write_json(output / "complete.json", complete)
    return 0 if completed else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(
            "protocol/experiments/bssc-joint-portfolio-wplus-k1-v2/manifest.json"
        ),
    )
    parser.add_argument("--seeds")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY") and "--dry-run" not in sys.argv:
        raise SystemExit("OPENROUTER_API_KEY is required unless --dry-run is used")
    raise SystemExit(run(parse_args(sys.argv[1:])))
