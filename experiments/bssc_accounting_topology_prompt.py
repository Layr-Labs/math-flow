"""Run an unpublished Builder V9 accounting-topology prompt ablation.

The experiment reads immutable BSSC validity-v4 bundles and canonical submission
evidence, then runs independent three-transition chains without publishing any
projection state. Provider output and reduced states are written only to the
requested artifact directory.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from typing import Mapping

from math_flow.artifacts import read_verified_artifact, sha256_bytes
from math_flow.bssc_research_v4_producer import (
    _accepted_frontier,
    _materialize_validity_bundle,
)
from math_flow.counterfactual_context import (
    accepted_claim_refs_from_validity,
    manifest_submission_at,
    reconstruct_submission_evidence,
)
from math_flow.errors import MathFlowError
from math_flow.governed_providers import OpenRouterResearchBuilderV9Provider
from math_flow.judges import load_source
from math_flow.judgments import load_judgment_bundle
from math_flow.openrouter import send_chat_completion
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v9 import apply_research_builder_v9_transition
from math_flow.research_projection import _accepted_claims
from math_flow.validity import validate_evidence_packet_v4
from math_flow.work_projection import SubmissionEvidenceFile


PROBLEM_ID = "bssc-sum-capacity"
VARIANTS = ("baseline", "accounting", "worked-example")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def normalized_accepted_claims(
    judgment: dict[str, object], packet: dict[str, object]
) -> list[dict[str, object]]:
    raw_claims = _accepted_claims(judgment, packet)
    return sorted(
        [
            {
                "claimKey": str(item["claimKey"]),
                "declaredStatement": str(item["statement"]),
                "validitySummary": str(item["validitySummary"]),
                "scopeQualifications": sorted(
                    {str(value) for value in item["scopeQualifications"]}
                ),
                "evidenceTransactionIds": sorted(
                    {str(value) for value in item["evidenceTransactionIds"]}
                ),
                "dependencyTransactionIds": sorted(
                    {str(value) for value in item["dependencyTransactionIds"]}
                ),
            }
            for item in raw_claims
        ],
        key=lambda item: str(item["claimKey"]),
    )


def materialize_case(
    root: Path,
    *,
    projection_commit: str,
    entry: Mapping[str, object],
    directory: Path,
) -> dict[str, object]:
    validity_dir = directory / "validity"
    _materialize_validity_bundle(
        root,
        projection_commit=projection_commit,
        entry=entry,
        destination=validity_dir,
    )
    manifest, judgment, _ = load_judgment_bundle(validity_dir)
    packet = json.loads(
        read_verified_artifact(
            validity_dir, manifest, "judgment-dependency-packet"
        )
    )
    validate_evidence_packet_v4(packet)
    claims = normalized_accepted_claims(judgment, packet)
    if not claims:
        raise MathFlowError("experimental case has no accepted claims")

    subject = str(entry["subjectTransactionId"])
    source = load_source(root, PROBLEM_ID, subject)
    transaction = next(
        (
            item
            for item in source["transactions"]
            if item.get("transactionId") == subject
        ),
        None,
    )
    if not isinstance(transaction, dict):
        raise MathFlowError("experimental subject is outside canonical ledger")
    evidence_manifest, chunks = manifest_submission_at(
        root,
        problem_id=PROBLEM_ID,
        subject_transaction_id=subject,
        contribution_path=str(transaction["path"]),
    )
    reconstructed = reconstruct_submission_evidence(evidence_manifest, chunks)
    evidence_files = tuple(
        SubmissionEvidenceFile(
            path=path,
            digest=sha256_bytes(content),
            content=content,
        )
        for path, content in sorted(reconstructed.items())
    )
    write_json(directory / "accepted-claims.json", claims)
    write_json(directory / "evidence-manifest.json", evidence_manifest)
    return {
        "subject": subject,
        "judgmentId": str(judgment["judgmentId"]),
        "judgment": judgment,
        "claims": claims,
        "acceptedClaimRefs": accepted_claim_refs_from_validity(
            judgment, subject_transaction_id=subject
        ),
        "evidenceManifest": evidence_manifest,
        "evidenceChunks": chunks,
        "evidenceFiles": evidence_files,
        "ledgerOrdinal": int(transaction["ordinal"]),
    }


def variant_spec(
    base: Mapping[str, object],
    additions: Mapping[str, object],
    *,
    variant: str,
    seed: int,
) -> dict[str, object]:
    spec = copy.deepcopy(dict(base))
    spec["id"] = f"openrouter-hierarchical-research-builder-v9-experiment-{variant}"
    parameters = dict(spec["parameters"])
    parameters["seed"] = seed
    spec["parameters"] = parameters
    policy = dict(spec["retryPolicy"])
    policy["maximumAttempts"] = 1
    spec["retryPolicy"] = policy
    if variant in {"accounting", "worked-example"}:
        spec["systemPrompt"] = (
            str(spec["systemPrompt"])
            + "\n\n<accounting-topology-guidance>\n"
            + str(additions["accounting"])
            + "\n</accounting-topology-guidance>"
        )
    if variant == "worked-example":
        spec["systemPrompt"] = (
            str(spec["systemPrompt"])
            + "\n\n<accounting-topology-worked-examples>\n"
            + str(additions["workedExample"])
            + "\n</accounting-topology-worked-examples>"
        )
    return spec


class CapturingTransport:
    def __init__(self) -> None:
        self.requests: list[dict[str, object]] = []
        self.responses: list[dict[str, object]] = []

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        response = send_chat_completion(request)
        self.responses.append(copy.deepcopy(response))
        return response


def state_summary(state: Mapping[str, object], subject: str) -> dict[str, object]:
    programs = state.get("programs")
    results = state.get("intermediateResults")
    contributions = state.get("contributions")
    program_rows = []
    if isinstance(programs, dict):
        for program_id, program in sorted(programs.items()):
            if not isinstance(program, dict):
                continue
            program_rows.append(
                {
                    "id": program_id,
                    "parentId": program.get("parentId"),
                    "title": program.get("title"),
                    "objective": program.get("objective"),
                    "status": program.get("status"),
                    "intermediateResultIds": program.get("intermediateResultIds"),
                }
            )
    result_rows = []
    if isinstance(results, dict):
        for result_id, result in sorted(results.items()):
            if not isinstance(result, dict):
                continue
            if subject not in result.get("sourceTransactionIds", []):
                continue
            result_rows.append(
                {
                    "id": result_id,
                    "title": result.get("title"),
                    "primaryProgramId": result.get("primaryProgramId"),
                    "relatedProgramIds": result.get("relatedProgramIds"),
                    "dependencyResultIds": result.get("dependencyResultIds"),
                    "claimRefs": result.get("claimRefs"),
                }
            )
    contribution = (
        contributions.get(subject)
        if isinstance(contributions, dict)
        else None
    )
    return {
        "stateDigest": state.get("stateDigest"),
        "ledgerHead": state.get("ledgerHead"),
        "programs": program_rows,
        "subjectResults": result_rows,
        "contribution": contribution,
    }


def request_summary(transport: CapturingTransport) -> dict[str, object] | None:
    if not transport.requests:
        return None
    request = transport.requests[-1]
    response = transport.responses[-1] if transport.responses else None
    messages = request.get("messages")
    return {
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
        "providerResponseId": response.get("id")
        if isinstance(response, dict)
        else None,
        "resolvedModel": response.get("model")
        if isinstance(response, dict)
        else None,
        "usage": response.get("usage") if isinstance(response, dict) else None,
    }


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    experiment_root = root / "protocol/experiments/bssc-credit-topology-v1"
    manifest = load_json(experiment_root / "manifest.json")
    additions = load_json(experiment_root / "prompt-additions.json")
    base_spec = load_json(
        root / "protocol/judges/openrouter-hierarchical-research-builder-v9.json"
    )
    source = load_json(
        root / "protocol/runtime/bssc-research-v4-validity-source-v1.json"
    )
    if not isinstance(manifest, dict) or not isinstance(additions, dict):
        raise MathFlowError("experimental manifest or prompt additions are invalid")
    if not isinstance(base_spec, dict) or not isinstance(source, dict):
        raise MathFlowError("experimental builder or validity source is invalid")
    pins, accepted = _accepted_frontier(root, source)
    selected = accepted[: args.cases]
    cases: list[dict[str, object]] = []
    for entry in selected:
        ordinal = int(entry["acceptedTransitionOrdinal"])
        cases.append(
            materialize_case(
                root,
                projection_commit=str(pins["projectionCommit"]),
                entry=entry,
                directory=output / "inputs" / f"k{ordinal}",
            )
        )

    variants = tuple(args.variants.split(","))
    unknown = sorted(set(variants) - set(VARIANTS))
    if unknown:
        raise MathFlowError(f"unknown experiment variant: {unknown[0]}")
    seeds = tuple(int(value) for value in args.seeds.split(","))
    plan = {
        "schemaVersion": 1,
        "experiment": manifest,
        "dryRun": args.dry_run,
        "mainCommit": pins["mainCommit"],
        "projectionCommit": pins["projectionCommit"],
        "variants": list(variants),
        "seeds": list(seeds),
        "subjects": [case["subject"] for case in cases],
        "plannedProviderCalls": 0 if args.dry_run else len(variants) * len(seeds) * len(cases),
    }
    write_json(output / "plan.json", plan)
    for variant in variants:
        for seed in seeds:
            spec = variant_spec(base_spec, additions, variant=variant, seed=seed)
            chain_dir = output / "chains" / variant / f"seed-{seed}"
            write_json(chain_dir / "judge-spec.json", spec)
            state = empty_research_program_state_v3(PROBLEM_ID)
            chain_summary: dict[str, object] = {
                "variant": variant,
                "seed": seed,
                "status": "dry-run" if args.dry_run else "running",
                "transitions": [],
            }
            if args.dry_run:
                write_json(chain_dir / "summary.json", chain_summary)
                continue
            for index, case in enumerate(cases, start=1):
                case_dir = chain_dir / f"k{index}"
                transport = CapturingTransport()
                journals: list[dict[str, object]] = []
                provider = OpenRouterResearchBuilderV9Provider(
                    spec,
                    transport=transport,
                    attempt_journal_writer=lambda value: journals.append(value),
                )
                record: dict[str, object] = {
                    "acceptedTransitionOrdinal": index,
                    "ledgerOrdinal": case["ledgerOrdinal"],
                    "subjectTransactionId": case["subject"],
                    "baseStateDigest": state["stateDigest"],
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
                            "postStateDigest": state["stateDigest"],
                            "request": request_summary(transport),
                            "invocations": provider.invocation_records,
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - experiment records failures
                    record.update(
                        {
                            "status": "failed",
                            "errorType": type(exc).__name__,
                            "error": str(exc),
                            "request": request_summary(transport),
                        }
                    )
                    if transport.responses:
                        write_json(case_dir / "provider-response.json", transport.responses[-1])
                    write_json(case_dir / "attempt-journals.json", journals)
                    chain_summary["transitions"].append(record)
                    chain_summary["status"] = "failed"
                    break
                write_json(case_dir / "attempt-journals.json", journals)
                chain_summary["transitions"].append(record)
            else:
                chain_summary["status"] = "completed"
            write_json(chain_dir / "summary.json", chain_summary)
    write_json(output / "complete.json", {**plan, "status": "completed"})
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variants", default=",".join(VARIANTS))
    parser.add_argument("--seeds", default="1729,2718")
    parser.add_argument("--cases", type=int, default=3, choices=range(1, 4))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY") and "--dry-run" not in sys.argv:
        raise SystemExit("OPENROUTER_API_KEY is required unless --dry-run is used")
    raise SystemExit(run(parse_args(sys.argv[1:])))
