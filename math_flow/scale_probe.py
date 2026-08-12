from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .artifacts import ArtifactBundle, load_manifest
from .context import materialize_agent_context
from .coordination import (
    claim_due_build,
    complete_build,
    fail_build,
    lane_id,
    load_scheduler,
    publish_batch,
    record_completed_inputs,
)
from .errors import MathFlowError
from .github_projection import _MAX_FILES_PER_COMMIT, _publication_plan
from .governance import resolve_projection
from .knowledge import empty_state_v3
from .projection_queue import merge_scheduler_states, validate_scheduler_state
from .repository import ledger, sha256_json
from .viewer import export_viewer_catalog


def _digest(*parts: object) -> str:
    return f"sha256:{sha256_json([str(part) for part in parts])}"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def _validate_configuration(
    problems: int,
    projections: int,
    solvers: int,
    minimum_interval_seconds: int,
    maximum_judgments_per_build: int,
) -> None:
    values = {
        "problems": problems,
        "projections": projections,
        "solvers": solvers,
        "minimum interval": minimum_interval_seconds,
        "maximum judgments per build": maximum_judgments_per_build,
    }
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value <= 0
        for value in values.values()
    ):
        raise MathFlowError("provider-free scale probe settings must be positive integers")
    lanes = problems * projections
    jobs = lanes * (solvers + (1 if solvers >= 2 else 0))
    if lanes > 5_000 or jobs > 100_000:
        raise MathFlowError(
            "provider-free scale probe is bounded to 5,000 lanes and 100,000 judgments"
        )
    if solvers >= 2 and maximum_judgments_per_build < 3:
        raise MathFlowError(
            "maximum judgments per build must be at least three when conflicts are modeled"
        )


def _dirty_lane(
    state: dict[str, object], identifier: str, judgment_id: str, now: int
) -> dict[str, object]:
    updated = copy.deepcopy(state)
    lane = updated["lanes"][identifier]
    lane["observedJudgmentIds"] = sorted(
        set(lane["observedJudgmentIds"]) | {judgment_id}
    )
    lane["pendingJudgmentIds"] = sorted(
        set(lane["pendingJudgmentIds"]) | {judgment_id}
    )
    lane["nextEligibleAt"] = now
    return validate_scheduler_state(updated)


def _build_discovery_fixture(
    root: Path, problem_count: int, projection_count: int
) -> dict[str, int]:
    repository = root / "catalog-repository"
    projection_root = root / "catalog-projections"
    repository.mkdir()
    _git(repository, "init", "-q")
    _git(repository, "config", "user.name", "Math Flow Scale Probe")
    _git(repository, "config", "user.email", "scale-probe@example.invalid")

    _write_json(
        repository / "protocol/judges/reconciliation.json",
        {"implementation": "openrouter-markdown-reconciliation-v1"},
    )
    builder_spec = {"implementation": "openrouter-knowledge-builder-v2"}
    _write_json(repository / "protocol/judges/builder.json", builder_spec)
    for projection_number in range(projection_count):
        projection_id = f"scale-projection-{projection_number:03d}"
        primary_path = f"protocol/judges/primary-{projection_number:03d}.json"
        _write_json(
            repository / primary_path,
            {
                "id": f"scale-primary-{projection_number:03d}",
                "implementation": "openrouter-markdown-judgment-v1",
            },
        )
        _write_json(
            repository / f"protocol/projections/{projection_id}.json",
            {
                "schemaVersion": 1,
                "id": projection_id,
                "description": "Provider-free scale discovery fixture",
                "status": "active",
                "engine": "openrouter-repository-v1",
                "allowedProblems": ["*"],
                "primaryJudge": primary_path,
                "reconciliationJudge": "protocol/judges/reconciliation.json",
                "knowledgeBuilder": "protocol/judges/builder.json",
                "scheduling": {
                    "judgmentMaxParallel": 16,
                    "knowledgeMinimumIntervalSeconds": 60,
                    "maximumJudgmentsPerBuild": 500,
                },
            },
        )
    for problem_number in range(problem_count):
        problem = f"scale-problem-{problem_number:03d}"
        path = repository / f"problems/{problem}/problem.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Scale problem {problem_number}\n", encoding="utf-8")
    _git(repository, "add", ".")
    _git(repository, "commit", "-qm", "Initialize provider-free discovery fixture")

    for problem_number in range(problem_count):
        problem = f"scale-problem-{problem_number:03d}"
        contribution = repository / f"problems/{problem}/contributions/solver-000/README.md"
        contribution.parent.mkdir(parents=True, exist_ok=True)
        contribution.write_text("# Deterministic contribution\n", encoding="utf-8")
        _git(repository, "add", str(contribution.relative_to(repository)))
        _git(repository, "commit", "-qm", f"Add contribution to {problem}")

    head = _git(repository, "rev-parse", "HEAD")
    builder_digest = f"sha256:{sha256_json(builder_spec)}"
    scheduler = projection_root / "coordination/scheduler.json"
    bundle_number = 0
    stream_ids: set[str] = set()
    for problem_number in range(problem_count):
        problem = f"scale-problem-{problem_number:03d}"
        source = ledger(repository, problem, head)
        for projection_number in range(projection_count):
            projection_id = f"scale-projection-{projection_number:03d}"
            resolved = resolve_projection(repository, projection_id, problem, head)
            stream_ids.add(str(resolved["judgmentStreamId"]))
            projection_digest = str(resolved["projectionSpecDigest"])
            # Use the protocol lane identity so context exercises the same
            # scheduler lookup as hosted runs.
            identifier = lane_id(problem, builder_digest, projection_digest)
            bundle = root / f"catalog-bundle-{bundle_number:04d}"
            bundle_number += 1
            writer = ArtifactBundle(bundle)
            writer.add_json(
                "state/state.json", empty_state_v3(problem), "knowledge-state"
            )
            writer.add_text(
                "state/revisions.jsonl",
                "",
                "knowledge-revisions",
                "application/x-ndjson",
            )
            writer.add_text("report.md", "# Knowledge state\n", "report", "text/markdown")
            writer.add_json(
                "control/selection.json",
                {"selectedNodeIds": [], "rationale": "Provider-free fixture."},
                "node-selection",
            )
            writer.add_json(
                "control/normalizations.json",
                {"normalizations": []},
                "adapter-normalizations",
            )
            writer.add_json(
                "state/delta.json", {"operations": []}, "knowledge-delta"
            )
            writer.finalize(
                {
                    "protocolVersion": 1,
                    "runKind": "knowledge-build",
                    "problemId": problem,
                    "ledgerHead": source["ledgerHead"],
                    "problemLedgerHead": source["problemLedgerHead"],
                    "problemLedgerDigest": source["problemLedgerDigest"],
                    "outputProfile": "math-flow/knowledge-build-markdown-v2",
                    "judgeSpec": {
                        "id": "scale-builder",
                        "digest": builder_digest,
                    },
                    "runner": {
                        "implementation": "provider-free-scale-probe",
                        "mathFlowVersion": "scale-probe-v1",
                    },
                    "baseRun": None,
                    "providerRuns": [],
                    "inputs": {
                        "laneId": identifier,
                        "problemId": problem,
                        "builderSpecDigest": builder_digest,
                        "projectionSpecDigest": projection_digest,
                    },
                }
            )
            _, run_digest = load_manifest(bundle)
            publish_batch(projection_root, [bundle])
            lane = record_completed_inputs(
                scheduler,
                problem,
                builder_digest,
                [_digest("catalog-judgment", problem, projection_id)],
                [],
                60,
                1_000,
                projection_digest,
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1_000, 1)
            if claim is None:
                raise MathFlowError("scale discovery fixture could not claim its lane")
            complete_build(
                scheduler,
                str(lane["laneId"]),
                str(claim["buildToken"]),
                run_digest,
                1_001,
            )

    catalog = export_viewer_catalog(
        repository,
        projection_root,
        "scale/fixture",
        canonical_ref=head,
    )
    expected = problem_count * projection_count
    if len(catalog["projections"]) != expected:
        raise MathFlowError("scale viewer catalog lost a problem/projection lane")
    materialized = 0
    for projection in catalog["projections"]:
        output = root / f"context-{materialized:04d}"
        summary = materialize_agent_context(
            repository,
            projection_root,
            str(projection["problemId"]),
            output,
            projection_id=str(projection["id"]),
            head=head,
        )
        if summary["freshness"] != "current":
            raise MathFlowError("scale context discovery produced a stale fixture")
        materialized += 1
    return {
        "sampleProblems": problem_count,
        "sampleProjectionsPerProblem": projection_count,
        "catalogEntries": len(catalog["projections"]),
        "materializedContexts": materialized,
        "independentJudgmentStreams": len(stream_ids),
    }


def run_provider_free_scale_probe(
    *,
    problems: int = 12,
    projections: int = 4,
    solvers: int = 12,
    minimum_interval_seconds: int = 300,
    maximum_judgments_per_build: int = 64,
) -> dict[str, object]:
    """Exercise scheduling, retries, publication, and discovery without a provider."""

    _validate_configuration(
        problems,
        projections,
        solvers,
        minimum_interval_seconds,
        maximum_judgments_per_build,
    )
    lane_count = problems * projections
    reconciliation_count = lane_count if solvers >= 2 else 0
    judgment_count = lane_count * solvers + reconciliation_count
    now = 10_000

    with tempfile.TemporaryDirectory(prefix="math-flow-scale-") as temporary:
        temporary_root = Path(temporary)
        scheduler = temporary_root / "scheduler.json"
        lane_specs: list[dict[str, object]] = []
        for problem_number in range(problems):
            problem = f"problem-{problem_number:04d}"
            for projection_number in range(projections):
                projection = f"projection-{projection_number:04d}"
                primary_ids = [
                    _digest("primary", problem, projection, solver_number)
                    for solver_number in range(solvers)
                ]
                conflict_id = (
                    _digest("conflict", problem, projection)
                    if solvers >= 2
                    else None
                )
                reconciliation_id = (
                    _digest("reconciliation", problem, projection)
                    if conflict_id is not None
                    else None
                )
                lane_specs.append(
                    {
                        "problem": problem,
                        "projection": projection,
                        "builderDigest": _digest("builder", projection),
                        "projectionDigest": _digest("projection", projection),
                        "primaryIds": primary_ids,
                        "conflictId": conflict_id,
                        "reconciliationId": reconciliation_id,
                    }
                )

        def record(spec: dict[str, object]) -> dict[str, object]:
            primary_ids = list(spec["primaryIds"])
            conflict_id = spec["conflictId"]
            reconciliation_id = spec["reconciliationId"]
            judgment_ids = [*primary_ids]
            conflict_ids: list[str] = []
            conflict_dependencies: dict[str, list[str]] = {}
            reconciliation_dependencies: dict[str, dict[str, object]] = {}
            if isinstance(conflict_id, str) and isinstance(reconciliation_id, str):
                judgment_ids.append(reconciliation_id)
                conflict_ids.append(conflict_id)
                conflict_dependencies[conflict_id] = primary_ids[:2]
                reconciliation_dependencies[reconciliation_id] = {
                    "conflictId": conflict_id,
                    "inputJudgmentIds": primary_ids[:2],
                }
            return record_completed_inputs(
                scheduler,
                str(spec["problem"]),
                str(spec["builderDigest"]),
                judgment_ids,
                conflict_ids,
                minimum_interval_seconds,
                now,
                str(spec["projectionDigest"]),
                conflict_dependencies,
                reconciliation_dependencies,
                _digest("ledger", spec["problem"]),
            )

        with ThreadPoolExecutor(max_workers=min(32, lane_count)) as executor:
            recorded = list(executor.map(record, lane_specs))
        for spec, lane in zip(lane_specs, recorded):
            spec["laneId"] = lane["laneId"]

        state = load_scheduler(scheduler)
        if len(state["lanes"]) != lane_count:
            raise MathFlowError("concurrent judgment completion lost a scheduler lane")

        requests = [
            (spec, attempt)
            for spec in lane_specs
            for attempt in range(2)
        ]

        def claim_once(item: tuple[dict[str, object], int]) -> tuple[str, dict[str, object] | None]:
            spec, _ = item
            identifier = str(spec["laneId"])
            return (
                identifier,
                claim_due_build(
                    scheduler,
                    identifier,
                    now,
                    maximum_judgments_per_build,
                ),
            )

        with ThreadPoolExecutor(max_workers=min(32, len(requests))) as executor:
            claimed = list(executor.map(claim_once, requests))
        claims: dict[str, dict[str, object]] = {}
        rejected_duplicate_claims = 0
        for identifier, claim in claimed:
            if claim is None:
                rejected_duplicate_claims += 1
            elif identifier in claims:
                raise MathFlowError("one knowledge lane granted two active leases")
            else:
                claims[identifier] = claim
        if len(claims) != lane_count or rejected_duplicate_claims != lane_count:
            raise MathFlowError("knowledge lane lease isolation failed under contention")

        all_claims: dict[str, list[dict[str, object]]] = {
            identifier: [claim] for identifier, claim in claims.items()
        }
        durable_failures = 0
        reset_failures = 0
        throttled_claims = 0
        for index, spec in enumerate(lane_specs):
            identifier = str(spec["laneId"])
            claim = claims[identifier]
            completed_at = now + 10
            mode = index % 11
            if mode == 0:
                durable_failures += 1
                failed = fail_build(
                    scheduler,
                    identifier,
                    str(claim["buildToken"]),
                    completed_at,
                    _digest("ledger", spec["problem"]),
                )
                retry_at = int(failed["nextEligibleAt"])
                if claim_due_build(
                    scheduler,
                    identifier,
                    retry_at - 1,
                    maximum_judgments_per_build,
                ) is not None:
                    raise MathFlowError("failed knowledge lane ignored durable backoff")
                retry = claim_due_build(
                    scheduler,
                    identifier,
                    retry_at,
                    maximum_judgments_per_build,
                )
                if retry is None:
                    raise MathFlowError("failed knowledge lane did not become retryable")
                all_claims[identifier].append(retry)
                complete_build(
                    scheduler,
                    identifier,
                    str(retry["buildToken"]),
                    _digest("state", identifier, 1),
                    retry_at,
                )
            elif mode == 1:
                reset_failures += 1
                fail_build(
                    scheduler,
                    identifier,
                    str(claim["buildToken"]),
                    completed_at,
                    _digest("ledger", spec["problem"]),
                )
                record_completed_inputs(
                    scheduler,
                    str(spec["problem"]),
                    str(spec["builderDigest"]),
                    [_digest("new-evidence", identifier)],
                    [],
                    minimum_interval_seconds,
                    completed_at + 1,
                    str(spec["projectionDigest"]),
                    problem_ledger_digest=_digest("ledger-advanced", spec["problem"]),
                )
                reset = claim_due_build(
                    scheduler,
                    identifier,
                    completed_at + 1,
                    maximum_judgments_per_build,
                )
                if reset is None:
                    raise MathFlowError("new evidence did not reset failed-lane backoff")
                all_claims[identifier].append(reset)
                complete_build(
                    scheduler,
                    identifier,
                    str(reset["buildToken"]),
                    _digest("state", identifier, 1),
                    completed_at + 1,
                )
            else:
                record_completed_inputs(
                    scheduler,
                    str(spec["problem"]),
                    str(spec["builderDigest"]),
                    [_digest("coalesced", identifier)],
                    [],
                    minimum_interval_seconds,
                    completed_at - 1,
                    str(spec["projectionDigest"]),
                )
                complete_build(
                    scheduler,
                    identifier,
                    str(claim["buildToken"]),
                    _digest("state", identifier, 1),
                    completed_at,
                )
                eligible_at = completed_at + minimum_interval_seconds
                if claim_due_build(
                    scheduler,
                    identifier,
                    eligible_at - 1,
                    maximum_judgments_per_build,
                ) is not None:
                    raise MathFlowError("knowledge lane ignored its minimum interval")
                throttled_claims += 1

        for spec in lane_specs:
            identifier = str(spec["laneId"])
            batch = len(all_claims[identifier])
            while True:
                lane = load_scheduler(scheduler)["lanes"][identifier]
                if lane["activeBuild"] is not None:
                    raise MathFlowError("scale probe left an unexpected active lease")
                if not lane["pendingJudgmentIds"] and not lane["pendingConflictIds"]:
                    break
                eligible_at = int(lane["nextEligibleAt"])
                next_claim = claim_due_build(
                    scheduler,
                    identifier,
                    eligible_at,
                    maximum_judgments_per_build,
                )
                if next_claim is None:
                    raise MathFlowError("eligible knowledge lane could not be drained")
                all_claims[identifier].append(next_claim)
                batch += 1
                complete_build(
                    scheduler,
                    identifier,
                    str(next_claim["buildToken"]),
                    _digest("state", identifier, batch),
                    eligible_at,
                )

        dependency_atomic_claims = 0
        dependency_atomic_lanes: set[str] = set()
        for spec in lane_specs:
            if not isinstance(spec["conflictId"], str):
                continue
            component = {
                *list(spec["primaryIds"])[:2],
                str(spec["reconciliationId"]),
                str(spec["conflictId"]),
            }
            for claim in all_claims[str(spec["laneId"])]:
                selected = set(claim["judgmentIds"]) | set(claim["conflictIds"])
                if selected & component:
                    if not component <= selected:
                        raise MathFlowError(
                            "reconciliation dependency component was split across builds"
                        )
                    dependency_atomic_claims += 1
                    dependency_atomic_lanes.add(str(spec["laneId"]))
        if len(dependency_atomic_lanes) != reconciliation_count:
            raise MathFlowError("a reconciliation dependency component was not formed")

        base = load_scheduler(scheduler)
        merged = copy.deepcopy(base)
        publication_judgments: dict[str, str] = {}
        for index, spec in enumerate(lane_specs):
            identifier = str(spec["laneId"])
            new_id = _digest("publication", identifier)
            publication_judgments[identifier] = new_id
            ours = _dirty_lane(base, identifier, new_id, 100_000 + index)
            merged = merge_scheduler_states(base, ours, merged)
        for identifier, new_id in publication_judgments.items():
            if new_id not in merged["lanes"][identifier]["pendingJudgmentIds"]:
                raise MathFlowError("optimistic merge lost a disjoint lane update")

        first_identifier = str(lane_specs[0]["laneId"])
        stale_ours = _dirty_lane(base, first_identifier, _digest("stale-ours"), 200_000)
        competing = _dirty_lane(base, first_identifier, _digest("competing"), 200_001)
        divergent_rejected = False
        try:
            merge_scheduler_states(base, stale_ours, competing)
        except MathFlowError as exc:
            divergent_rejected = "changed divergently" in str(exc)
        if not divergent_rejected:
            raise MathFlowError("stale same-lane publication was not rejected")
        refreshed = _dirty_lane(
            competing, first_identifier, _digest("stale-ours"), 200_002
        )
        converged = merge_scheduler_states(competing, refreshed, competing)
        if _digest("stale-ours") not in converged["lanes"][first_identifier][
            "pendingJudgmentIds"
        ]:
            raise MathFlowError("stale publication did not converge after refresh")

        immutable_paths: list[str] = []
        for number in range(judgment_count):
            for artifact in ("run.json", "record.json", "report.md"):
                immutable_paths.append(
                    f"objects/judgment/{number:08x}/{artifact}"
                )
        for number in range(lane_count):
            for artifact_number in range(7):
                immutable_paths.append(
                    f"objects/knowledge-build/{number:08x}/artifact-{artifact_number}.json"
                )
            immutable_paths.append(f"publication-batches/{number:08x}.json")
        additions = [
            {"path": path, "contents": ""} for path in immutable_paths
        ]
        additions.extend(
            [
                {"path": "coordination/scheduler.json", "contents": ""},
                {"path": "viewer/catalog.json", "contents": ""},
                *[
                    {
                        "path": f"indexes/problems/problem-{number:04d}/runs.json",
                        "contents": "",
                    }
                    for number in range(problems)
                ],
            ]
        )
        plan = _publication_plan(additions, [])
        immutable_commits = sum(phase == "immutable" for phase, _, _ in plan)
        metadata_commits = sum(phase == "metadata" for phase, _, _ in plan)
        if any(
            len(phase_additions) + len(phase_deletions) > _MAX_FILES_PER_COMMIT
            for _, phase_additions, phase_deletions in plan
        ):
            raise MathFlowError("projection publication plan exceeded its commit bound")

        discovery = _build_discovery_fixture(
            temporary_root,
            min(problems, 2),
            min(projections, 2),
        )
        scheduler_bytes = scheduler.stat().st_size

    return {
        "schemaVersion": 1,
        "status": "passed",
        "providerCalls": 0,
        "configuration": {
            "problems": problems,
            "projectionsPerProblem": projections,
            "solversPerProblemProjection": solvers,
            "minimumIntervalSeconds": minimum_interval_seconds,
            "maximumJudgmentsPerBuild": maximum_judgments_per_build,
        },
        "judgmentAndFormation": {
            "knowledgeLanes": lane_count,
            "independentJudgmentStreams": lane_count,
            "primaryJudgmentJobs": lane_count * solvers,
            "reconciliationJobs": reconciliation_count,
            "simultaneousActiveBuildsAcrossLanes": lane_count,
            "duplicateSameLaneClaimsRejected": rejected_duplicate_claims,
            "dependencyAtomicClaims": dependency_atomic_claims,
            "minimumIntervalClaimsSuppressed": throttled_claims,
            "durableFailureRetries": durable_failures,
            "newEvidenceFailureResets": reset_failures,
            "schedulerBytes": scheduler_bytes,
        },
        "publication": {
            "disjointLaneUpdatesMerged": lane_count,
            "staleSameLaneUpdatesRejected": 1,
            "staleUpdatesConvergedAfterRefresh": 1,
            "immutableFiles": len(immutable_paths),
            "immutableCommits": immutable_commits,
            "metadataCommits": metadata_commits,
            "maximumFilesPerCommit": _MAX_FILES_PER_COMMIT,
            "bulkMetadataFiles": problems + 2,
        },
        "discovery": discovery,
        "verifiedInvariants": {
            "judgmentCompletionsPreserveEveryLane": True,
            "knowledgeIsSingleWriterPerLane": True,
            "knowledgeLanesDoNotBlockOneAnother": True,
            "reconciliationDependenciesAreAtomic": True,
            "formationIsThrottled": True,
            "failuresAndRetriesAreLaneLocal": True,
            "disjointPublicationIsMergeable": True,
            "staleSameLanePublicationFailsClosed": True,
            "publicationIsChunkBounded": True,
            "viewerAndContextDiscoverEverySampleLane": True,
        },
    }
