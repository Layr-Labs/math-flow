"""Run the unpublished sequential BSSC K2/K3 local Builder V10 experiment."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Mapping

from experiments.bssc_accounting_topology_holdout import (
    PROBLEM_ID,
    TRANSITION_ORDINALS,
    _accepted_entry_by_ordinal,
    response_summaries,
)
from experiments.bssc_accounting_topology_prompt import (
    load_json,
    materialize_case,
    state_summary,
    write_json,
)
from math_flow.bssc_research_v4_producer import _accepted_frontier
from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.openrouter import send_chat_completion
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.research_builder_v10 import apply_research_builder_v10_transition
from math_flow.research_builder_v10_provider import (
    OpenRouterResearchBuilderV10Provider,
)
from math_flow.teacher_student_scenarios import (
    ScenarioArtifact,
    _score_json_relational,
)


class BudgetedCapturingTransport:
    def __init__(
        self,
        *,
        maximum_calls: int,
        maximum_cost_usd: float,
        maximum_single_call_cost_usd: float,
        maximum_request_bytes: int,
        maximum_total_tokens: int,
        transport: Callable[[dict[str, object]], dict[str, object]] = send_chat_completion,
    ) -> None:
        self.requests: list[dict[str, object]] = []
        self.responses: list[dict[str, object]] = []
        self.maximum_calls = maximum_calls
        self.maximum_cost_usd = maximum_cost_usd
        self.maximum_single_call_cost_usd = maximum_single_call_cost_usd
        self.maximum_request_bytes = maximum_request_bytes
        self.maximum_total_tokens = maximum_total_tokens
        self.transport = transport
        self.blocked_reason: str | None = None

    @property
    def reported_cost_usd(self) -> float:
        total = 0.0
        for response in self.responses:
            usage = response.get("usage")
            if isinstance(usage, dict) and isinstance(usage.get("cost"), (int, float)):
                total += float(usage["cost"])
        return total

    @property
    def reported_total_tokens(self) -> int:
        return sum(
            int(response["usage"]["total_tokens"])
            for response in self.responses
            if isinstance(response.get("usage"), dict)
            and isinstance(response["usage"].get("total_tokens"), int)
            and not isinstance(response["usage"].get("total_tokens"), bool)
        )

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        if self.blocked_reason is not None:
            raise MathFlowError(self.blocked_reason)
        if len(self.requests) >= self.maximum_calls:
            raise MathFlowError("local Builder V10 experiment provider-call budget exhausted")
        request_bytes = len(
            json.dumps(
                request,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )
        if request_bytes > self.maximum_request_bytes:
            raise MathFlowError(
                "local Builder V10 experiment request budget exhausted: "
                f"{request_bytes} > {self.maximum_request_bytes} bytes"
            )
        maximum_completion_tokens = request.get("max_tokens")
        if (
            isinstance(maximum_completion_tokens, bool)
            or not isinstance(maximum_completion_tokens, int)
            or maximum_completion_tokens < 1
        ):
            raise MathFlowError(
                "local Builder V10 request has no positive completion-token ceiling"
            )
        reserved_tokens = request_bytes + maximum_completion_tokens
        if self.reported_total_tokens + reserved_tokens > self.maximum_total_tokens:
            raise MathFlowError(
                "local Builder V10 experiment total-token budget exhausted"
            )
        if (
            self.reported_cost_usd + self.maximum_single_call_cost_usd
            > self.maximum_cost_usd
        ):
            raise MathFlowError("local Builder V10 experiment cost budget exhausted")
        self.requests.append(copy.deepcopy(request))
        try:
            response = self.transport(copy.deepcopy(request))
        except Exception:
            self.blocked_reason = (
                "local Builder V10 transport outcome is uncertain; further spending is blocked"
            )
            raise
        self.responses.append(copy.deepcopy(response))
        usage = response.get("usage")
        cost = usage.get("cost") if isinstance(usage, dict) else None
        if (
            isinstance(cost, bool)
            or not isinstance(cost, (int, float))
            or not math.isfinite(float(cost))
            or float(cost) < 0
        ):
            self.blocked_reason = (
                "local Builder V10 response omitted valid cost telemetry; further spending is blocked"
            )
            raise MathFlowError(self.blocked_reason)
        assert isinstance(usage, dict)
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            token_count = usage.get(field)
            if (
                isinstance(token_count, bool)
                or not isinstance(token_count, int)
                or token_count < 0
            ):
                self.blocked_reason = (
                    "local Builder V10 response omitted valid token telemetry; "
                    "further spending is blocked"
                )
                raise MathFlowError(self.blocked_reason)
        if (
            int(usage["prompt_tokens"]) > request_bytes
            or int(usage["completion_tokens"]) > maximum_completion_tokens
            or int(usage["total_tokens"]) > reserved_tokens
            or self.reported_total_tokens > self.maximum_total_tokens
        ):
            self.blocked_reason = (
                "local Builder V10 response exceeded a reserved token ceiling; "
                "further spending is blocked"
            )
            raise MathFlowError(self.blocked_reason)
        if float(cost) > self.maximum_single_call_cost_usd:
            self.blocked_reason = (
                "local Builder V10 response exceeded the reserved single-call cost ceiling; "
                "further spending is blocked"
            )
            raise MathFlowError(self.blocked_reason)
        if self.reported_cost_usd > self.maximum_cost_usd:
            self.blocked_reason = (
                "local Builder V10 response exceeded the total cost ceiling; further spending is blocked"
            )
            raise MathFlowError(self.blocked_reason)
        return response


def candidate_spec(
    base: Mapping[str, object], *, seed: int, maximum_attempts: int
) -> dict[str, object]:
    spec = copy.deepcopy(dict(base))
    spec["id"] = "openrouter-hierarchical-research-builder-v10-bssc-holdout"
    parameters = dict(spec["parameters"])
    parameters["seed"] = seed
    spec["parameters"] = parameters
    retry = dict(spec["retryPolicy"])
    retry["maximumAttempts"] = maximum_attempts
    spec["retryPolicy"] = retry
    return spec


def _usage_totals(responses: list[dict[str, object]]) -> dict[str, object]:
    fields = ("prompt_tokens", "completion_tokens", "total_tokens")
    totals: dict[str, object] = {field: 0 for field in fields}
    totals["reasoning_tokens"] = 0
    totals["cost"] = 0.0
    for response in responses:
        usage = response.get("usage")
        if not isinstance(usage, dict):
            continue
        for field in fields:
            value = usage.get(field)
            if isinstance(value, int):
                totals[field] = int(totals[field]) + value
        details = usage.get("completion_tokens_details")
        if isinstance(details, dict) and isinstance(details.get("reasoning_tokens"), int):
            totals["reasoning_tokens"] = int(totals["reasoning_tokens"]) + int(
                details["reasoning_tokens"]
            )
        if isinstance(usage.get("cost"), (int, float)):
            totals["cost"] = float(totals["cost"]) + float(usage["cost"])
    return totals


def _scenario_artifact(value: object) -> ScenarioArtifact:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return ScenarioArtifact(value=value, digest=sha256_bytes(raw), media_type="application/json")


def _serialized_measurement(value: object) -> dict[str, int]:
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return {
        "characters": len(serialized),
        "utf8Bytes": len(serialized.encode("utf-8")),
    }


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise MathFlowError(
            "local Builder V10 experiment output directory must be new or empty"
        )
    output.mkdir(parents=True, exist_ok=True)
    experiment_root = root / "protocol/experiments/bssc-local-builder-v10-v1"
    manifest = load_json(experiment_root / "manifest.json")
    base_spec = load_json(
        root
        / "protocol/judges/openrouter-hierarchical-research-builder-v10-experiment.json"
    )
    source = load_json(
        root / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
    )
    if not all(isinstance(value, dict) for value in (manifest, base_spec, source)):
        raise MathFlowError("local Builder V10 experiment configuration is invalid")
    if manifest.get("problemId") != PROBLEM_ID:
        raise MathFlowError("local Builder V10 manifest names another problem")
    configured_ordinals = tuple(
        int(value) for value in manifest.get("acceptedTransitionOrdinals", [])
    )
    if configured_ordinals != TRANSITION_ORDINALS:
        raise MathFlowError("local Builder V10 manifest ordinals do not match the runner")
    if base_spec.get("model") != manifest.get("model"):
        raise MathFlowError("local Builder V10 manifest model does not match the judge")
    configured_effort = manifest.get("reasoningEffort")
    stages = base_spec.get("stages")
    if not isinstance(stages, dict) or any(
        not isinstance(stages.get(stage), dict)
        or stages[stage].get("parameters", {}).get("reasoning", {}).get("effort")
        != configured_effort
        for stage in ("route", "route-refine", "organize")
    ):
        raise MathFlowError(
            "local Builder V10 manifest reasoning effort does not match the judge"
        )

    def load_bound_gold(path_field: str, digest_field: str) -> object:
        path = (root / str(manifest[path_field])).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise MathFlowError("local Builder V10 gold path escapes the repository") from exc
        raw = path.read_bytes()
        if sha256_bytes(raw) != manifest.get(digest_field):
            raise MathFlowError(f"local Builder V10 {path_field} digest mismatch")
        return json.loads(raw) if path.suffix == ".json" else raw.decode("utf-8")

    relational_gold = load_bound_gold("relationalGold", "relationalGoldDigest")
    load_bound_gold("semanticGold", "semanticGoldDigest")
    if not isinstance(relational_gold, dict) or not isinstance(
        relational_gold.get("assertions"), list
    ):
        raise MathFlowError("local Builder V10 relational gold is invalid")
    advisory_ids = {
        str(value) for value in manifest.get("relationalAdvisoryAssertionIds", [])
    }
    observed_advisory_ids: set[str] = set()
    relational_gold = copy.deepcopy(relational_gold)
    for assertion in relational_gold["assertions"]:
        if isinstance(assertion, dict) and assertion.get("id") in advisory_ids:
            assertion["severity"] = "advisory"
            observed_advisory_ids.add(str(assertion["id"]))
    if observed_advisory_ids != advisory_ids:
        raise MathFlowError(
            "local Builder V10 advisory assertion policy names an unknown assertion"
        )

    fixed = manifest.get("fixedBase")
    if not isinstance(fixed, dict):
        raise MathFlowError("local Builder V10 fixed base is invalid")
    fixed_base = validate_research_program_state_v3(
        load_json(root / str(fixed["fixture"])), PROBLEM_ID
    )
    if (
        fixed_base["stateDigest"] != fixed.get("stateDigest")
        or fixed_base["ledgerHead"] != fixed.get("ledgerHead")
    ):
        raise MathFlowError("local Builder V10 fixed base binding mismatch")
    write_json(output / "fixed-base-state.json", fixed_base)

    pins, accepted = _accepted_frontier(root, source)
    cases = [
        materialize_case(
            root,
            projection_commit=str(pins["projectionCommit"]),
            entry=_accepted_entry_by_ordinal(accepted, ordinal),
            directory=output / "inputs" / f"k{ordinal}",
        )
        for ordinal in TRANSITION_ORDINALS
    ]
    configured_seeds = tuple(int(value) for value in manifest.get("seeds", []))
    seeds = (
        configured_seeds
        if args.seeds is None
        else tuple(int(value) for value in args.seeds.split(","))
    )
    if not seeds or len(seeds) != len(set(seeds)) or not set(seeds) <= set(configured_seeds):
        raise MathFlowError("local Builder V10 requested seeds are outside the manifest")
    maximum_attempts = int(manifest["maximumAttemptsPerStage"])
    maximum_calls = int(manifest["maximumProviderCalls"])
    maximum_cost = float(manifest["maximumReportedCostUsd"])
    maximum_single_call_cost = float(manifest["maximumSingleCallCostUsd"])
    maximum_request_bytes = int(manifest["maximumRequestBytes"])
    maximum_total_tokens = int(manifest["maximumTotalProviderTokens"])
    plan = {
        "schemaVersion": 1,
        "experiment": manifest,
        "dryRun": args.dry_run,
        "mainCommit": pins["mainCommit"],
        "projectionCommit": pins["projectionCommit"],
        "seeds": list(seeds),
        "subjects": [case["subject"] for case in cases],
        "maximumAttemptsPerStage": maximum_attempts,
        "maximumProviderCalls": 0 if args.dry_run else maximum_calls,
        "maximumReportedCostUsd": maximum_cost,
        "maximumSingleCallCostUsd": maximum_single_call_cost,
        "maximumRequestBytes": maximum_request_bytes,
        "maximumTotalProviderTokens": maximum_total_tokens,
        "relationalGold": manifest["relationalGold"],
        "relationalGoldDigest": manifest["relationalGoldDigest"],
        "semanticGold": manifest["semanticGold"],
        "semanticGoldDigest": manifest["semanticGoldDigest"],
    }
    write_json(output / "plan.json", plan)
    transport = BudgetedCapturingTransport(
        maximum_calls=maximum_calls,
        maximum_cost_usd=maximum_cost,
        maximum_single_call_cost_usd=maximum_single_call_cost,
        maximum_request_bytes=maximum_request_bytes,
        maximum_total_tokens=maximum_total_tokens,
    )
    chains: list[dict[str, object]] = []

    for seed in seeds:
        state = copy.deepcopy(fixed_base)
        chain_dir = output / "chains" / f"seed-{seed}"
        spec = candidate_spec(
            base_spec, seed=seed, maximum_attempts=maximum_attempts
        )
        write_json(chain_dir / "judge-spec.json", spec)
        chain: dict[str, object] = {
            "seed": seed,
            "status": "dry-run" if args.dry_run else "running",
            "fixedBaseStateDigest": fixed_base["stateDigest"],
            "transitions": [],
        }
        score_registry: dict[str, ScenarioArtifact] = {
            "fixed-base-state": _scenario_artifact(fixed_base)
        }
        if args.dry_run:
            write_json(chain_dir / "summary.json", chain)
            chains.append(chain)
            continue

        for ordinal, case in zip(TRANSITION_ORDINALS, cases, strict=True):
            case_dir = chain_dir / f"k{ordinal}"
            request_start = len(transport.requests)
            response_start = len(transport.responses)
            journals: list[dict[str, object]] = []
            provider = OpenRouterResearchBuilderV10Provider(
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
                if not isinstance(provider.latest_artifacts, dict):
                    raise MathFlowError("local Builder V10 artifacts are unavailable")
                evidence_bytes = sum(
                    len(evidence.content) for evidence in case["evidenceFiles"]
                )
                record["contextTelemetry"] = {
                    "acceptedClaimAssessments": _serialized_measurement(case["claims"]),
                    "route": {
                        "routeContext": _serialized_measurement(
                            provider.latest_artifacts["routeContext"]
                        ),
                        "submissionEvidenceBytes": 0,
                    },
                    "route-refine": {
                        "discoveryPacket": _serialized_measurement(
                            provider.latest_artifacts["discoveryPacket"]
                        ),
                        "submissionEvidenceBytes": 0,
                    },
                    "organize": {
                        "authoringPacket": _serialized_measurement(
                            provider.latest_artifacts["authoringPacket"]
                        ),
                        "submissionEvidenceBytes": evidence_bytes,
                        "submissionEvidenceFileCount": len(case["evidenceFiles"]),
                    },
                }
                reduced = apply_research_builder_v10_transition(
                    state,
                    transition,
                    authoring_packet=provider.latest_artifacts["authoringPacket"],
                    accepted_claims=case["claims"],
                    judgment_id=str(case["judgmentId"]),
                    evidence_file_refs={
                        evidence.path: evidence.digest
                        for evidence in case["evidenceFiles"]
                    },
                )
                state = reduced["postState"]
                for name, value in provider.latest_artifacts.items():
                    write_json(case_dir / f"{name}.json", value)
                write_json(case_dir / "state.json", state)
                topology_summary = state_summary(state, str(case["subject"]))
                write_json(case_dir / "topology-summary.json", topology_summary)
                score_registry[f"k{ordinal}.author.transition"] = _scenario_artifact(
                    transition
                )
                score_registry[f"k{ordinal}.author.topology"] = _scenario_artifact(
                    topology_summary
                )
                record.update(
                    {
                        "status": "accepted",
                        "providerCalls": len(transport.requests) - request_start,
                        "postStateDigest": state["stateDigest"],
                        "invocations": provider.invocation_records,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - preserve experiment failures
                record.update(
                    {
                        "status": "failed",
                        "providerCalls": len(transport.requests) - request_start,
                        "errorType": type(exc).__name__,
                        "error": str(exc),
                    }
                )
            requests = transport.requests[request_start:]
            responses = transport.responses[response_start:]
            write_json(case_dir / "provider-requests.json", requests)
            write_json(case_dir / "provider-responses.json", responses)
            write_json(case_dir / "attempt-journals.json", journals)
            record["responses"] = response_summaries(
                type(
                    "Captured",
                    (),
                    {"requests": requests, "responses": responses},
                )()
            )
            record["requestTelemetry"] = [
                {
                    **_serialized_measurement(request),
                    "maxTokens": request.get("max_tokens"),
                }
                for request in requests
            ]
            record["usage"] = _usage_totals(responses)
            write_json(case_dir / "summary.json", record)
            chain["transitions"].append(record)
            if record["status"] != "accepted":
                chain["status"] = "failed"
                break
        else:
            chain["status"] = "completed"
            chain["relationalScore"] = _score_json_relational(
                relational_gold,
                score_registry,
                variant="local-builder-v10",
                seed=seed,
                scorer_id="bssc-accounting-topology-v3",
            )
            write_json(chain_dir / "relational-score.json", chain["relationalScore"])
            if chain["relationalScore"].get("status") != "passed":
                chain["status"] = "evaluation-failed"
        chain["providerCalls"] = sum(
            int(item.get("providerCalls", 0))
            for item in chain["transitions"]
            if isinstance(item, dict)
        )
        write_json(chain_dir / "summary.json", chain)
        chains.append(chain)

    completed = all(
        chain.get("status") in {"completed", "dry-run"} for chain in chains
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
    parser.add_argument("--seeds")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY") and "--dry-run" not in sys.argv:
        raise SystemExit("OPENROUTER_API_KEY is required unless --dry-run is used")
    raise SystemExit(run(parse_args(sys.argv[1:])))
