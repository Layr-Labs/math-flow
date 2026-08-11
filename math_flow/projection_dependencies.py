from __future__ import annotations

import json
from pathlib import Path

from .artifacts import verify_bundle
from .coordination import load_scheduler
from .errors import MathFlowError
from .governance import resolve_projection
from .projection_queue import validate_scheduler_state
from .repository import ledger, read_at, sha256_json


SUPPORTED_DEPENDENCY_ROLES = {"knowledge-state"}


def _artifact_for_role(
    manifest: dict[str, object], role: str
) -> dict[str, object]:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise MathFlowError("projection dependency run has an invalid artifact index")
    matches = [
        item
        for item in artifacts
        if isinstance(item, dict) and item.get("role") == role
    ]
    if len(matches) != 1:
        raise MathFlowError(
            f"projection dependency run must contain exactly one {role!r} artifact"
        )
    artifact = matches[0]
    required = {"path", "role", "mediaType", "digest", "bytes"}
    if set(artifact) != required:
        raise MathFlowError(
            f"projection dependency artifact {role!r} has an invalid manifest entry"
        )
    return {key: artifact[key] for key in sorted(required)}


def _knowledge_state_dependency(
    projection_root: Path,
    scheduler: dict[str, object],
    dependency: dict[str, object],
    problem: str,
    problem_ledger: dict[str, object],
    expected_builder_digest: str,
) -> dict[str, object]:
    projection_digest = str(dependency["projectionSpecDigest"])
    lanes = [
        lane
        for lane in scheduler["lanes"].values()
        if lane.get("problemId") == problem
        and lane.get("projectionSpecDigest") == projection_digest
    ]
    if len(lanes) != 1:
        raise MathFlowError(
            f"projection dependency {dependency['name']!r} must resolve to exactly "
            f"one knowledge lane; found {len(lanes)}"
        )
    lane = lanes[0]
    if lane.get("activeBuild") is not None:
        raise MathFlowError(
            f"projection dependency {dependency['name']!r} has an active build"
        )
    if lane.get("pendingJudgmentIds") or lane.get("pendingConflictIds"):
        raise MathFlowError(
            f"projection dependency {dependency['name']!r} has pending knowledge inputs"
        )
    run_digest = lane.get("latestStateRun")
    if not isinstance(run_digest, str):
        raise MathFlowError(
            f"projection dependency {dependency['name']!r} has no published state"
        )
    digest_hex = run_digest.removeprefix("sha256:")
    bundle = (
        projection_root
        / "objects"
        / "knowledge-build"
        / digest_hex[:2]
        / digest_hex
    )
    if not bundle.is_dir() or bundle.is_symlink():
        raise MathFlowError(
            f"projection dependency run is not published: {run_digest}"
        )
    manifest, actual_digest = verify_bundle(bundle)
    if actual_digest != run_digest:
        raise MathFlowError(
            "projection dependency run does not match its content address: "
            f"{run_digest}"
        )
    inputs = manifest.get("inputs")
    judge_spec = manifest.get("judgeSpec")
    if (
        manifest.get("runKind") != "knowledge-build"
        or manifest.get("problemId") != problem
        or not isinstance(inputs, dict)
        or inputs.get("problemId") != problem
        or inputs.get("laneId") != lane.get("laneId")
        or inputs.get("projectionSpecDigest") != projection_digest
        or lane.get("builderSpecDigest") != expected_builder_digest
        or inputs.get("builderSpecDigest") != expected_builder_digest
        or not isinstance(judge_spec, dict)
        or judge_spec.get("digest") != expected_builder_digest
    ):
        raise MathFlowError(
            f"projection dependency run does not match {dependency['projectionId']!r}"
        )
    expected_ledger_digest = problem_ledger["problemLedgerDigest"]
    if manifest.get("problemLedgerDigest") != expected_ledger_digest:
        raise MathFlowError(
            f"projection dependency {dependency['name']!r} is stale for the "
            "current problem ledger"
        )
    problem_ledger_head = manifest.get("problemLedgerHead")
    ledger_head = manifest.get("ledgerHead")
    if not isinstance(problem_ledger_head, str) or not isinstance(ledger_head, str):
        raise MathFlowError("projection dependency run has invalid ledger provenance")

    artifact = _artifact_for_role(manifest, str(dependency["artifactRole"]))
    return {
        **dependency,
        "runKind": "knowledge-build",
        "runDigest": run_digest,
        "ledgerHead": ledger_head,
        "problemLedgerHead": problem_ledger_head,
        "problemLedgerDigest": expected_ledger_digest,
        "artifact": artifact,
    }


def resolve_projection_dependencies(
    root: Path,
    projection_root: Path,
    projection: str,
    problem: str,
    head: str = "HEAD",
) -> dict[str, object]:
    """Resolve governed dependency declarations to verified immutable run inputs.

    The returned lock is suitable for inclusion by digest in a downstream run
    manifest. It deliberately rejects stale state and lanes with unfinished
    formation work, so an overlay cannot race its declared knowledge input.
    """

    root = root.resolve()
    projection_root = projection_root.resolve()
    consumer = resolve_projection(root, projection, problem, head)
    if consumer["canonicalHead"] == "WORKTREE":
        raise MathFlowError(
            "projection dependency locks require a commit-addressed canonical head"
        )
    problem_ledger = ledger(root, problem, str(consumer["canonicalHead"]))
    scheduler = validate_scheduler_state(
        load_scheduler(projection_root / "coordination" / "scheduler.json")
    )

    resolved: list[dict[str, object]] = []
    for dependency in consumer["dependencies"]:
        role = str(dependency["artifactRole"])
        if role not in SUPPORTED_DEPENDENCY_ROLES:
            raise MathFlowError(
                f"projection dependency role is not supported by this runner: {role}"
            )
        producer = resolve_projection(
            root,
            str(dependency["projectionId"]),
            problem,
            str(consumer["canonicalHead"]),
        )
        builder_path = producer.get("knowledgeBuilder")
        if not isinstance(builder_path, str):
            raise MathFlowError(
                f"projection dependency {dependency['name']!r} has no knowledge builder"
            )
        try:
            builder_spec = json.loads(
                read_at(
                    root,
                    str(consumer["canonicalHead"]),
                    builder_path,
                )
            )
        except json.JSONDecodeError as exc:
            raise MathFlowError(
                f"projection dependency builder is not valid JSON: {builder_path}"
            ) from exc
        if not isinstance(builder_spec, dict):
            raise MathFlowError(
                f"projection dependency builder must be an object: {builder_path}"
            )
        expected_builder_digest = f"sha256:{sha256_json(builder_spec)}"
        resolved.append(
            _knowledge_state_dependency(
                projection_root,
                scheduler,
                dependency,
                problem,
                problem_ledger,
                expected_builder_digest,
            )
        )

    core = {
        "schemaVersion": 1,
        "consumer": {
            "projectionId": consumer["projectionId"],
            "projectionSpecDigest": consumer["projectionSpecDigest"],
            "problemId": problem,
            "canonicalHead": consumer["canonicalHead"],
        },
        "problemLedger": {
            "problemLedgerHead": problem_ledger["problemLedgerHead"],
            "problemLedgerDigest": problem_ledger["problemLedgerDigest"],
        },
        "dependencies": resolved,
    }
    return {
        **core,
        "dependencyLockDigest": f"sha256:{sha256_json(core)}",
    }
