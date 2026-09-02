"""Run the unpublished sequential K2/K3 accounting-topology holdout."""

from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path
from typing import Mapping

from experiments.bssc_accounting_topology_prompt import (
    CapturingTransport,
    load_json,
    materialize_case,
    state_summary,
    write_json,
)
from math_flow.bssc_research_v4_producer import _accepted_frontier
from math_flow.errors import MathFlowError
from math_flow.governed_providers import OpenRouterResearchBuilderV9Provider
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.research_builder_v9 import apply_research_builder_v9_transition


PROBLEM_ID = "bssc-sum-capacity"
TRANSITION_ORDINALS = (2, 3)


def candidate_spec(
    base: Mapping[str, object],
    additions: Mapping[str, object],
    *,
    seed: int,
    maximum_attempts: int,
) -> dict[str, object]:
    spec = copy.deepcopy(dict(base))
    spec["id"] = "openrouter-hierarchical-research-builder-v9-accounting-holdout"
    parameters = dict(spec["parameters"])
    parameters["seed"] = seed
    spec["parameters"] = parameters
    policy = dict(spec["retryPolicy"])
    policy["maximumAttempts"] = maximum_attempts
    spec["retryPolicy"] = policy
    spec["systemPrompt"] = (
        str(spec["systemPrompt"])
        + "\n\n<accounting-topology-guidance>\n"
        + str(additions["accounting"])
        + "\n</accounting-topology-guidance>"
        + "\n\n<generalized-accounting-topology-controls>\n"
        + str(additions["candidate"])
        + "\n</generalized-accounting-topology-controls>"
    )
    return spec


def response_summaries(transport: CapturingTransport) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for index, response in enumerate(transport.responses):
        request = transport.requests[index]
        messages = request.get("messages")
        summaries.append(
            {
                "attempt": index + 1,
                "model": request.get("model"),
                "seed": request.get("seed"),
                "reasoning": request.get("reasoning"),
                "maxTokens": request.get("max_tokens"),
                "messageCharacters": [
                    len(str(item.get("content", "")))
                    for item in messages
                    if isinstance(item, dict)
                ]
                if isinstance(messages, list)
                else None,
                "providerResponseId": response.get("id"),
                "resolvedModel": response.get("model"),
                "finishReason": (
                    response.get("choices", [{}])[0].get("finish_reason")
                    if isinstance(response.get("choices"), list)
                    and response["choices"]
                    and isinstance(response["choices"][0], dict)
                    else None
                ),
                "usage": response.get("usage"),
            }
        )
    return summaries


def _accepted_entry_by_ordinal(
    accepted: list[dict[str, object]], ordinal: int
) -> dict[str, object]:
    entry = next(
        (
            item
            for item in accepted
            if int(item["acceptedTransitionOrdinal"]) == ordinal
        ),
        None,
    )
    if not isinstance(entry, dict):
        raise MathFlowError(f"accepted transition {ordinal} is unavailable")
    return entry


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    experiment_root = root / "protocol/experiments/bssc-credit-topology-v3"
    manifest = load_json(experiment_root / "manifest.json")
    additions = load_json(experiment_root / "prompt-additions.json")
    base_spec = load_json(
        root / "protocol/judges/openrouter-hierarchical-research-builder-v9.json"
    )
    source = load_json(
        root / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
    )
    if not all(
        isinstance(value, dict)
        for value in (manifest, additions, base_spec, source)
    ):
        raise MathFlowError("holdout experiment configuration is invalid")

    fixed = manifest.get("fixedBase")
    if not isinstance(fixed, dict):
        raise MathFlowError("holdout fixed-base declaration is invalid")
    fixture = root / str(fixed["fixture"])
    fixed_base = validate_research_program_state_v3(
        load_json(fixture), PROBLEM_ID
    )
    if fixed_base["stateDigest"] != fixed.get("stateDigest"):
        raise MathFlowError("holdout fixed-base state digest mismatch")
    if fixed_base["ledgerHead"] != fixed.get("ledgerHead"):
        raise MathFlowError("holdout fixed-base ledger head mismatch")
    write_json(output / "fixed-base-state.json", fixed_base)

    pins, accepted = _accepted_frontier(root, source)
    cases: list[dict[str, object]] = []
    for ordinal in TRANSITION_ORDINALS:
        entry = _accepted_entry_by_ordinal(accepted, ordinal)
        cases.append(
            materialize_case(
                root,
                projection_commit=str(pins["projectionCommit"]),
                entry=entry,
                directory=output / "inputs" / f"k{ordinal}",
            )
        )

    seeds = tuple(int(value) for value in args.seeds.split(","))
    maximum_attempts = int(manifest["maximumAttempts"])
    plan = {
        "schemaVersion": 1,
        "experiment": manifest,
        "dryRun": args.dry_run,
        "mainCommit": pins["mainCommit"],
        "projectionCommit": pins["projectionCommit"],
        "fixedBaseStateDigest": fixed_base["stateDigest"],
        "fixedBaseLedgerHead": fixed_base["ledgerHead"],
        "seeds": list(seeds),
        "subjects": [case["subject"] for case in cases],
        "maximumAttempts": maximum_attempts,
        "plannedTransitions": len(seeds) * len(cases),
        "maximumProviderCalls": (
            0
            if args.dry_run
            else len(seeds) * len(cases) * maximum_attempts
        ),
    }
    write_json(output / "plan.json", plan)
    chain_summaries: list[dict[str, object]] = []

    for seed in seeds:
        chain_dir = output / "chains" / f"seed-{seed}"
        spec = candidate_spec(
            base_spec,
            additions,
            seed=seed,
            maximum_attempts=maximum_attempts,
        )
        write_json(chain_dir / "judge-spec.json", spec)
        state = copy.deepcopy(fixed_base)
        chain: dict[str, object] = {
            "seed": seed,
            "status": "dry-run" if args.dry_run else "running",
            "fixedBaseStateDigest": fixed_base["stateDigest"],
            "transitions": [],
        }
        if args.dry_run:
            write_json(chain_dir / "summary.json", chain)
            chain_summaries.append(chain)
            continue

        for ordinal, case in zip(TRANSITION_ORDINALS, cases, strict=True):
            case_dir = chain_dir / f"k{ordinal}"
            transport = CapturingTransport()
            journals: list[dict[str, object]] = []
            provider = OpenRouterResearchBuilderV9Provider(
                spec,
                transport=transport,
                attempt_journal_writer=lambda value: journals.append(value),
            )
            record: dict[str, object] = {
                "acceptedTransitionOrdinal": ordinal,
                "ledgerOrdinal": case["ledgerOrdinal"],
                "subjectTransactionId": case["subject"],
                "baseStateDigest": state["stateDigest"],
                "status": "running",
            }
            try:
                transition = provider.run(
                    problem_id=PROBLEM_ID,
                    subject_transaction_id=str(case["subject"]),
                    base_state=state,
                    accepted_claims=case["claims"],
                    judgment_id=str(case["judgmentId"]),
                    evidence_files=case["evidenceFiles"],
                )
                reduced = apply_research_builder_v9_transition(
                    state,
                    transition,
                    accepted_claims=case["claims"],
                    judgment_id=str(case["judgmentId"]),
                    evidence_file_refs={
                        evidence.path: evidence.digest
                        for evidence in case["evidenceFiles"]
                    },
                )
                state = reduced["postState"]
                write_json(case_dir / "transition.json", transition)
                write_json(case_dir / "state.json", state)
                write_json(
                    case_dir / "topology-summary.json",
                    state_summary(state, str(case["subject"])),
                )
                record.update(
                    {
                        "status": "accepted",
                        "attempts": len(transport.requests),
                        "postStateDigest": state["stateDigest"],
                        "invocations": provider.invocation_records,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - preserve holdout failures
                record.update(
                    {
                        "status": "failed",
                        "attempts": len(transport.requests),
                        "errorType": type(exc).__name__,
                        "error": str(exc),
                    }
                )
            write_json(case_dir / "attempt-journals.json", journals)
            write_json(case_dir / "provider-responses.json", transport.responses)
            record["responses"] = response_summaries(transport)
            write_json(case_dir / "summary.json", record)
            chain["transitions"].append(record)
            if record["status"] != "accepted":
                chain["status"] = "failed"
                break
        else:
            chain["status"] = "completed"
        chain["providerCalls"] = sum(
            int(item.get("attempts", 0))
            for item in chain["transitions"]
            if isinstance(item, dict)
        )
        write_json(chain_dir / "summary.json", chain)
        chain_summaries.append(chain)

    write_json(
        output / "complete.json",
        {**plan, "status": "completed", "chains": chain_summaries},
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="1729,2718")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY") and "--dry-run" not in sys.argv:
        raise SystemExit("OPENROUTER_API_KEY is required unless --dry-run is used")
    raise SystemExit(run(parse_args(sys.argv[1:])))
