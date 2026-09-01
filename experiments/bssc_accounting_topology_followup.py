"""Run the unpublished fixed-K1 accounting-topology follow-up."""

from __future__ import annotations

import argparse
import copy
import json
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
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v9 import apply_research_builder_v9_transition


PROBLEM_ID = "bssc-sum-capacity"
VARIANTS = ("accounting", "refined-accounting")


def variant_spec(
    base: Mapping[str, object],
    additions: Mapping[str, object],
    *,
    variant: str,
    seed: int,
    maximum_attempts: int,
) -> dict[str, object]:
    spec = copy.deepcopy(dict(base))
    spec["id"] = f"openrouter-hierarchical-research-builder-v9-followup-{variant}"
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
    )
    if variant == "refined-accounting":
        spec["systemPrompt"] = (
            str(spec["systemPrompt"])
            + "\n\n<accounting-topology-followup-controls>\n"
            + str(additions["refinement"])
            + "\n</accounting-topology-followup-controls>"
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


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    experiment_root = root / "protocol/experiments/bssc-credit-topology-v2"
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
        raise MathFlowError("follow-up experiment configuration is invalid")

    pins, accepted = _accepted_frontier(root, source)
    case = materialize_case(
        root,
        projection_commit=str(pins["projectionCommit"]),
        entry=accepted[0],
        directory=output / "input" / "k1",
    )
    variants = tuple(args.variants.split(","))
    unknown = sorted(set(variants) - set(VARIANTS))
    if unknown:
        raise MathFlowError(f"unknown follow-up variant: {unknown[0]}")
    seeds = tuple(int(value) for value in args.seeds.split(","))
    maximum_attempts = int(manifest["maximumAttempts"])
    plan = {
        "schemaVersion": 1,
        "experiment": manifest,
        "dryRun": args.dry_run,
        "mainCommit": pins["mainCommit"],
        "projectionCommit": pins["projectionCommit"],
        "subjectTransactionId": case["subject"],
        "variants": list(variants),
        "seeds": list(seeds),
        "maximumAttempts": maximum_attempts,
        "plannedEvaluations": len(variants) * len(seeds),
        "maximumProviderCalls": (
            0
            if args.dry_run
            else len(variants) * len(seeds) * maximum_attempts
        ),
    }
    write_json(output / "plan.json", plan)
    summaries: list[dict[str, object]] = []

    for variant in variants:
        for seed in seeds:
            run_dir = output / "evaluations" / variant / f"seed-{seed}"
            spec = variant_spec(
                base_spec,
                additions,
                variant=variant,
                seed=seed,
                maximum_attempts=maximum_attempts,
            )
            write_json(run_dir / "judge-spec.json", spec)
            record: dict[str, object] = {
                "variant": variant,
                "seed": seed,
                "subjectTransactionId": case["subject"],
                "status": "dry-run" if args.dry_run else "running",
            }
            if args.dry_run:
                write_json(run_dir / "summary.json", record)
                summaries.append(record)
                continue

            state = empty_research_program_state_v3(PROBLEM_ID)
            transport = CapturingTransport()
            journals: list[dict[str, object]] = []
            provider = OpenRouterResearchBuilderV9Provider(
                spec,
                transport=transport,
                attempt_journal_writer=lambda value: journals.append(value),
            )
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
                post_state = reduced["postState"]
                write_json(run_dir / "transition.json", transition)
                write_json(run_dir / "state.json", post_state)
                write_json(
                    run_dir / "topology-summary.json",
                    state_summary(post_state, str(case["subject"])),
                )
                record.update(
                    {
                        "status": "accepted",
                        "attempts": len(transport.requests),
                        "postStateDigest": post_state["stateDigest"],
                        "invocations": provider.invocation_records,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - preserve experiment failures
                record.update(
                    {
                        "status": "failed",
                        "attempts": len(transport.requests),
                        "errorType": type(exc).__name__,
                        "error": str(exc),
                    }
                )
            write_json(run_dir / "attempt-journals.json", journals)
            write_json(run_dir / "provider-responses.json", transport.responses)
            record["responses"] = response_summaries(transport)
            write_json(run_dir / "summary.json", record)
            summaries.append(record)

    write_json(
        output / "complete.json",
        {**plan, "status": "completed", "evaluations": summaries},
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variants", default=",".join(VARIANTS))
    parser.add_argument("--seeds", default="1729,2718,3141")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY") and "--dry-run" not in sys.argv:
        raise SystemExit("OPENROUTER_API_KEY is required unless --dry-run is used")
    raise SystemExit(run(parse_args(sys.argv[1:])))
