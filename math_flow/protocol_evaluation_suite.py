"""Provider-free umbrella verification for the protocol-evaluation ladder.

The suite is deliberately an allowlisted local verifier, not an experiment
execution surface.  It accepts neither a provider transport nor publication
authority.  Every component must report zero provider calls, network use, and
publication attempts before the aggregate can pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping

from .artifacts import sha256_bytes, verify_bundle
from .builder_scale import (
    SyntheticBuilderStateConfig,
    build_bounded_exact_context_view,
    build_bounded_semantic_context_view,
    build_v9_context_view,
    make_v10_context_strategy,
    run_provider_free_builder_context_scale_probe,
)
from .errors import MathFlowError
from .no_three_shadow import build_no_three_v10_v2_shadow_preflight
from .repository import sha256_json
from .research_builder_v10 import (
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_route_context,
)
from .research_builder_v10_widening import (
    load_bound_widening_spec,
    load_widening_manifest,
    plan_widening_experiment,
)
from .teacher_student_scenarios import run_teacher_student_scenario
from .work_accounting_local_slice_probe import run_local_slice_probe
from .work_accounting_scale import (
    WorkAccountingScaleConfig,
    run_provider_free_work_accounting_scale_probe,
)


SUITE_ID = "protocol-evaluation-suite-v1"
DEFAULT_MANIFEST_PATH = Path(
    "protocol/experiments/protocol-evaluation-suite-v1/manifest.json"
)
MODES = ("pr", "full")


@dataclass(frozen=True)
class ComponentContext:
    root: Path
    mode: str
    checked_path: Path
    checked_raw: bytes


ComponentRunner = Callable[[ComponentContext], dict[str, object]]


def _pretty_json_bytes(value: object, *, sort_keys: bool) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=sort_keys, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _object_digest(value: object) -> str:
    return "sha256:" + sha256_json(value)


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be an object")
    return value


def _safe_repository_file(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise MathFlowError(f"{label} must be a repository-relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise MathFlowError(f"{label} must be a repository-relative path")
    repository = root.resolve()
    cursor = repository
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise MathFlowError(f"{label} may not traverse a symlink")
    resolved = repository.joinpath(*relative.parts).resolve()
    try:
        resolved.relative_to(repository)
    except ValueError as exc:
        raise MathFlowError(f"{label} escapes the repository") from exc
    if not resolved.is_file():
        raise MathFlowError(f"{label} does not exist")
    return resolved


def _resolve_manifest_path(root: Path, manifest_path: Path | str) -> Path:
    requested = Path(manifest_path)
    if requested.is_absolute():
        resolved = requested.resolve()
        try:
            relative = resolved.relative_to(root.resolve()).as_posix()
        except ValueError as exc:
            raise MathFlowError("protocol-evaluation manifest escapes the repository") from exc
    else:
        relative = requested.as_posix()
    return _safe_repository_file(root, relative, "protocol-evaluation manifest")


def load_protocol_evaluation_suite_manifest(
    root: Path,
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
) -> tuple[dict[str, object], str, str]:
    """Load the additive suite manifest and reject every authority surface."""

    repository = root.resolve()
    manifest_file = _resolve_manifest_path(repository, manifest_path)
    try:
        raw = manifest_file.read_bytes()
        manifest = json.loads(raw)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise MathFlowError("protocol-evaluation manifest is unreadable") from exc
    manifest = _mapping(manifest, "protocol-evaluation manifest")
    expected_fields = {
        "schemaVersion",
        "id",
        "status",
        "description",
        "publicationForbidden",
        "networkForbidden",
        "providerExecutionAuthorized",
        "credentialInputsAccepted",
        "executionFlagsAccepted",
        "acceptedModes",
        "extensionPolicy",
        "components",
    }
    if set(manifest) != expected_fields:
        raise MathFlowError("protocol-evaluation manifest has invalid fields")
    if (
        manifest.get("schemaVersion") != 1
        or manifest.get("id") != SUITE_ID
        or manifest.get("status") != "provider-free-local-verification"
        or manifest.get("publicationForbidden") is not True
        or manifest.get("networkForbidden") is not True
        or manifest.get("providerExecutionAuthorized") is not False
        or manifest.get("credentialInputsAccepted") != []
        or manifest.get("executionFlagsAccepted") != []
        or manifest.get("acceptedModes") != list(MODES)
    ):
        raise MathFlowError(
            "protocol-evaluation suite must remain provider-free and authority-free"
        )
    extension = _mapping(
        manifest.get("extensionPolicy"), "protocol-evaluation extension policy"
    )
    if extension != {
        "componentEnvelopeVersion": 1,
        "additiveRegistryEntriesAllowed": True,
    }:
        raise MathFlowError("protocol-evaluation extension policy is invalid")
    components = manifest.get("components")
    if not isinstance(components, list) or not components:
        raise MathFlowError("protocol-evaluation manifest needs components")
    observed: list[str] = []
    for index, value in enumerate(components, start=1):
        component = _mapping(value, f"protocol-evaluation component {index}")
        if set(component) != {
            "id",
            "checkedArtifact",
            "prVerification",
            "fullVerification",
        }:
            raise MathFlowError(
                f"protocol-evaluation component {index} has invalid fields"
            )
        identifier = component.get("id")
        if not isinstance(identifier, str) or identifier not in COMPONENT_RUNNERS:
            raise MathFlowError(
                f"protocol-evaluation component {index} is not allowlisted"
            )
        observed.append(identifier)
        checked = _mapping(
            component.get("checkedArtifact"),
            f"protocol-evaluation component {identifier} checked artifact",
        )
        if set(checked) != {"path", "digest"}:
            raise MathFlowError(
                f"protocol-evaluation component {identifier} checked artifact is invalid"
            )
        _safe_repository_file(
            repository,
            checked.get("path"),
            f"protocol-evaluation component {identifier} checked artifact",
        )
        digest = checked.get("digest")
        if (
            not isinstance(digest, str)
            or len(digest) != 71
            or not digest.startswith("sha256:")
            or any(character not in "0123456789abcdef" for character in digest[7:])
        ):
            raise MathFlowError(
                f"protocol-evaluation component {identifier} digest is invalid"
            )
        for field in ("prVerification", "fullVerification"):
            if not isinstance(component.get(field), str) or not component[field]:
                raise MathFlowError(
                    f"protocol-evaluation component {identifier} {field} is invalid"
                )
    if observed != list(COMPONENT_ORDER) or len(observed) != len(set(observed)):
        raise MathFlowError(
            "protocol-evaluation components must match the allowlisted order"
        )
    relative = manifest_file.relative_to(repository).as_posix()
    return manifest, relative, sha256_bytes(raw)


def _builder_strategies() -> dict[str, object]:
    return {
        "v9-all-core": build_v9_context_view,
        "bounded-semantic-model": build_bounded_semantic_context_view,
        "bounded-exact-provenance": build_bounded_exact_context_view,
        "v10-actual": make_v10_context_strategy(
            build_research_builder_v10_route_context,
            build_research_builder_v10_authoring_packet,
        ),
    }


def _require_exact_bytes(regenerated: bytes, checked: bytes, label: str) -> None:
    if regenerated != checked:
        raise MathFlowError(f"{label} does not exactly regenerate")


def _load_bssc_local_builder_v10_api(
    root: Path,
) -> tuple[Callable[[list[str]], object], Callable[[object], int]]:
    """Load the repository-only experiment without breaking installed CLI imports.

    ``experiments`` is intentionally not part of the distributable ``math_flow``
    package.  Keeping this import local means every other CLI command remains
    usable from an installed wheel, while the repository-bound umbrella suite
    can still call the experiment's public ``parse_args`` and ``run`` API.
    """

    script = _safe_repository_file(
        root,
        "experiments/bssc_local_builder_v10.py",
        "BSSC local Builder V10 experiment",
    )
    module_name = "_math_flow_protocol_evaluation_bssc_local_builder_v10"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise MathFlowError("BSSC local Builder V10 experiment is not importable")
    module = importlib.util.module_from_spec(spec)
    previous_module = sys.modules.get(module_name)
    repository_entry = str(root)
    sys.path.insert(0, repository_entry)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise MathFlowError("BSSC local Builder V10 experiment is not importable") from exc
    finally:
        if sys.path and sys.path[0] == repository_entry:
            sys.path.pop(0)
        else:
            try:
                sys.path.remove(repository_entry)
            except ValueError:
                pass
        if previous_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module
    parse_arguments = getattr(module, "parse_args", None)
    run_experiment = getattr(module, "run", None)
    if not callable(parse_arguments) or not callable(run_experiment):
        raise MathFlowError("BSSC local Builder V10 experiment API is incomplete")
    return parse_arguments, run_experiment


def _run_builder_context_scale(context: ComponentContext) -> dict[str, object]:
    configurations = None
    verification = "exact-regeneration"
    if context.mode == "pr":
        configurations = (
            SyntheticBuilderStateConfig(16, 24, 3, 3, 1, 2, 2),
        )
        verification = "bounded-smoke-plus-locked-full-report"
    report = run_provider_free_builder_context_scale_probe(
        configurations,
        input_budget_tokens=128_000,
        strategies=_builder_strategies(),
    )
    if report.get("status") != "passed" or report.get("providerCalls") != 0:
        raise MathFlowError("builder context-scale probe did not pass provider-free")
    if context.mode == "full":
        _require_exact_bytes(
            _pretty_json_bytes(report, sort_keys=True),
            context.checked_raw,
            "builder context-scale report",
        )
    return {
        "verification": verification,
        "outputDigest": _object_digest(report),
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {
            "caseCount": len(report["cases"]),
            "allGoldPlansPass": report["verifiedInvariants"][
                "goldAdversarialPlansPass"
            ],
        },
    }


def _run_builder_v10_widening_plan(context: ComponentContext) -> dict[str, object]:
    manifest = load_widening_manifest(
        context.checked_path, repository_root=context.root
    )
    spec = load_bound_widening_spec(manifest, repository_root=context.root)
    plan = plan_widening_experiment(manifest, spec=spec)
    if (
        plan.get("mode") != "provider-free-plan"
        or plan.get("providerCalls") != 0
        or plan.get("publicationForbidden") is not True
        or plan.get("providerExecutionDefault") != "disabled"
    ):
        raise MathFlowError("V10 widening plan crossed its provider-free boundary")
    return {
        "verification": "exact-provider-free-plan",
        "outputDigest": plan["planDigest"],
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {"caseCount": len(plan["cases"])},
    }


def _run_bssc_v10_k2_dry_run(context: ComponentContext) -> dict[str, object]:
    parse_arguments, run_experiment = _load_bssc_local_builder_v10_api(context.root)
    with tempfile.TemporaryDirectory(prefix="math-flow-bssc-v10-k2-dry-run-") as temporary:
        output = Path(temporary) / "output"
        arguments = parse_arguments(
            [
                "--root",
                str(context.root),
                "--output",
                str(output),
                "--manifest",
                str(context.checked_path),
                "--dry-run",
            ]
        )
        exit_status = run_experiment(arguments)
        try:
            complete_raw = (output / "complete.json").read_bytes()
            complete = json.loads(complete_raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise MathFlowError("BSSC V10 K2 dry-run produced no complete plan") from exc
    experiment = _mapping(complete.get("experiment"), "BSSC V10 K2 experiment")
    chains = complete.get("chains")
    if (
        exit_status != 0
        or complete.get("status") != "completed"
        or complete.get("dryRun") is not True
        or complete.get("providerCalls") != 0
        or complete.get("maximumProviderCalls") != 0
        or experiment.get("id") != "bssc-local-builder-v10-v2"
        or experiment.get("publicationForbidden") is not True
        or experiment.get("acceptedTransitionOrdinals") != [2]
        or experiment.get("seeds") != [1729]
        or complete.get("subjects") is None
        or not isinstance(chains, list)
        or len(chains) != 1
        or chains[0].get("status") != "dry-run"
    ):
        raise MathFlowError("BSSC final V2 K2-only dry-run is not exact")
    return {
        "verification": "exact-final-v2-k2-only-dry-run",
        "outputDigest": sha256_bytes(complete_raw),
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {
            "experimentId": experiment["id"],
            "acceptedTransitionOrdinals": [2],
            "seeds": [1729],
            "subjectCount": len(complete["subjects"]),
        },
    }


def _run_miniature_v10_v2_replay(context: ComponentContext) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="math-flow-miniature-suite-") as temporary:
        output = Path(temporary) / "bundle"
        run = run_teacher_student_scenario(
            context.root, context.checked_path, output
        )
        verified, run_digest = verify_bundle(output)
    execution = _mapping(run.get("execution"), "miniature execution")
    summary = _mapping(run.get("summary"), "miniature summary")
    if (
        verified != run
        or summary.get("status") != "passed"
        or summary.get("hardFailures") != 0
        or execution.get("providerCallsExecuted") != 0
        or execution.get("publicationForbidden") is not True
    ):
        raise MathFlowError("miniature V10/V2 teacher-student replay did not pass")
    return {
        "verification": "require-pass-exact-fixture-replay",
        "outputDigest": run_digest,
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {
            "scenarioId": summary.get("scenarioId", run["scenario"]["id"]),
            "chains": summary["chains"],
            "hardFailures": 0,
        },
    }


def _run_work_accounting_context_scale(
    context: ComponentContext,
) -> dict[str, object]:
    configurations = None
    scenarios = None
    verification = "exact-regeneration"
    if context.mode == "pr":
        configurations = (
            WorkAccountingScaleConfig(
                16, 24, 3, 4, evidence_bytes=512
            ),
        )
        scenarios = ("dependency-closure", "broad-local-subtree")
        verification = "bounded-smoke-plus-locked-full-report"
    keyword: dict[str, object] = {"input_budget_tokens": 128_000}
    if scenarios is not None:
        keyword["scenarios"] = scenarios
    report = run_provider_free_work_accounting_scale_probe(
        configurations,
        **keyword,
    )
    if (
        report.get("providerCalls") != 0
        or report.get("networkUsed") is not False
        or report.get("summary", {}).get("allSemanticAdversarialChecksPass")
        is not True
    ):
        raise MathFlowError(
            "work-accounting context-scale probe did not pass provider-free"
        )
    if context.mode == "full":
        _require_exact_bytes(
            _pretty_json_bytes(report, sort_keys=True),
            context.checked_raw,
            "work-accounting context-scale report",
        )
    return {
        "verification": verification,
        "outputDigest": report["reportDigest"],
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {
            "caseCount": report["caseCount"],
            "allSemanticAdversarialChecksPass": True,
        },
    }


def _run_work_accounting_local_slice(
    context: ComponentContext,
) -> dict[str, object]:
    configurations = None
    scenarios = (
        "direct",
        "dependency",
        "subtree",
        "topology-alignment",
        "completed-node",
        "broad-scope",
    )
    verification = "exact-regeneration"
    if context.mode == "pr":
        configurations = (WorkAccountingScaleConfig(16, 24, 3, 4),)
        scenarios = ("direct", "topology-alignment", "completed-node")
        verification = "bounded-smoke-plus-locked-full-report"
    report = run_local_slice_probe(configurations, scenarios=scenarios)
    summary = _mapping(report.get("summary"), "local accounting-slice summary")
    if (
        report.get("providerCalls") != 0
        or report.get("networkUsed") is not False
        or summary.get("allAttemptedRootTotalChecksMatch") is not True
        or int(summary.get("boundedRootTotalMatchCaseCount", 0)) < 1
    ):
        raise MathFlowError(
            "local accounting-slice probe did not pass provider-free"
        )
    if context.mode == "full":
        _require_exact_bytes(
            _pretty_json_bytes(report, sort_keys=True),
            context.checked_raw,
            "local accounting-slice report",
        )
    return {
        "verification": verification,
        "outputDigest": report["reportDigest"],
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {
            "caseCount": summary["caseCount"],
            "boundedRootTotalMatchCaseCount": summary[
                "boundedRootTotalMatchCaseCount"
            ],
            "explicitWideningCaseCount": summary[
                "explicitWideningCaseCount"
            ],
            "allAttemptedRootTotalChecksMatch": True,
        },
    }


def _run_no_three_v10_v2_preflight(
    context: ComponentContext,
) -> dict[str, object]:
    preflight = build_no_three_v10_v2_shadow_preflight(context.root)
    _require_exact_bytes(
        _pretty_json_bytes(preflight, sort_keys=False),
        context.checked_raw,
        "No-Three V10/V2 preflight",
    )
    if (
        preflight.get("providerCallCount") != 0
        or preflight.get("providerExecutionAuthorized") is not False
        or preflight.get("publicationForbidden") is not True
        or preflight.get("productionMutationForbidden") is not True
    ):
        raise MathFlowError("No-Three preflight crossed its zero-call boundary")
    return {
        "verification": "exact-zero-call-preflight-regeneration",
        "outputDigest": preflight["planDigest"],
        "providerCalls": 0,
        "networkUsed": False,
        "publicationAttempted": False,
        "details": {
            "subjectCount": len(preflight["inputBindings"]["subjects"]),
            "serialStageCount": len(preflight["serialExecutionPlan"]),
        },
    }


# Additive extension point: a later provider-free component adds one allowlisted
# runner and one manifest record.  The component and suite envelopes stay v1.
COMPONENT_RUNNERS: dict[str, ComponentRunner] = {
    "builder-context-scale": _run_builder_context_scale,
    "builder-v10-widening-plan": _run_builder_v10_widening_plan,
    "bssc-v10-k2-dry-run": _run_bssc_v10_k2_dry_run,
    "miniature-v10-v2-replay": _run_miniature_v10_v2_replay,
    "work-accounting-context-scale": _run_work_accounting_context_scale,
    "work-accounting-local-slice": _run_work_accounting_local_slice,
    "no-three-v10-v2-preflight": _run_no_three_v10_v2_preflight,
}
COMPONENT_ORDER = tuple(COMPONENT_RUNNERS)


def _prepare_output_directory(path: Path) -> Path:
    output = path.resolve()
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise MathFlowError(
                "protocol-evaluation output directory must be new or empty"
            )
    output.mkdir(parents=True, exist_ok=True)
    return output


def _render_markdown(summary: Mapping[str, object]) -> str:
    authority = _mapping(summary.get("authority"), "protocol-evaluation authority")
    authority_line = (
        "- Authority: 0 provider calls; no network or publication"
        if authority.get("providerCalls") == 0
        and authority.get("networkUsed") is False
        and authority.get("publicationAttempted") is False
        else "- Authority: unverified after a component failure; suite failed closed"
    )
    lines = [
        "# Provider-free protocol evaluation suite",
        "",
        f"- Status: **{summary['status']}**",
        f"- Mode: `{summary['mode']}`",
        f"- Components: {summary['passedComponents']}/{summary['componentCount']} passed",
        f"- Duration: {summary['durationMs']} ms",
        authority_line,
        "",
        "| Component | Status | Verification | Duration | Output digest |",
        "| --- | --- | --- | ---: | --- |",
    ]
    components = summary.get("components", [])
    assert isinstance(components, list)
    for component in components:
        assert isinstance(component, dict)
        lines.append(
            "| {id} | {status} | {verification} | {duration} ms | `{digest}` |".format(
                id=component["id"],
                status=component["status"],
                verification=component.get("verification", "not-run"),
                duration=component["durationMs"],
                digest=component.get("outputDigest", "n/a"),
            )
        )
        failure = component.get("failure")
        if isinstance(failure, dict):
            lines.extend(
                [
                    "",
                    f"Failure `{component['id']}`: {failure['class']}: {failure['summary']}",
                ]
            )
    lines.extend(
        [
            "",
            f"Summary digest: `{summary['summaryDigest']}`",
            "",
            "The suite accepts no credentials or provider-execution flag. Checked",
            "artifact drift and any nonzero external-effect report fail the suite.",
            "",
        ]
    )
    return "\n".join(lines)


def run_provider_free_protocol_evaluation_suite(
    root: Path,
    output_dir: Path,
    *,
    mode: str = "pr",
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
    clock_ns: Callable[[], int] = time.monotonic_ns,
) -> dict[str, object]:
    """Run the allowlisted provider-free suite and write JSON plus Markdown."""

    repository = root.resolve()
    if mode not in MODES:
        raise MathFlowError("protocol-evaluation mode must be pr or full")
    manifest, manifest_relative, manifest_digest = (
        load_protocol_evaluation_suite_manifest(repository, manifest_path)
    )
    output = _prepare_output_directory(output_dir)
    component_records: list[dict[str, object]] = []
    suite_start = clock_ns()
    for raw_component in manifest["components"]:
        component = _mapping(raw_component, "validated protocol-evaluation component")
        identifier = str(component["id"])
        checked = _mapping(
            component["checkedArtifact"], f"{identifier} checked artifact"
        )
        checked_path = _safe_repository_file(
            repository, checked["path"], f"{identifier} checked artifact"
        )
        checked_raw = checked_path.read_bytes()
        expected_digest = str(checked["digest"])
        actual_digest = sha256_bytes(checked_raw)
        started = clock_ns()
        record: dict[str, object] = {
            "id": identifier,
            "status": "running",
            "checkedArtifact": {
                "path": checked["path"],
                "expectedDigest": expected_digest,
                "actualDigest": actual_digest,
                "bytes": len(checked_raw),
            },
        }
        component_invoked = False
        try:
            if actual_digest != expected_digest:
                raise MathFlowError(f"{identifier} checked artifact digest drift")
            component_invoked = True
            outcome = COMPONENT_RUNNERS[identifier](
                ComponentContext(
                    root=repository,
                    mode=mode,
                    checked_path=checked_path,
                    checked_raw=checked_raw,
                )
            )
            if (
                outcome.get("providerCalls") != 0
                or outcome.get("networkUsed") is not False
                or outcome.get("publicationAttempted") is not False
            ):
                raise MathFlowError(
                    f"{identifier} reported a forbidden external effect"
                )
            record.update({"status": "passed", **outcome})
        except Exception as exc:  # noqa: BLE001 - preserve a fail-closed summary
            record.update(
                {
                    "status": "failed",
                    "verification": (
                        component["prVerification"]
                        if mode == "pr"
                        else component["fullVerification"]
                    ),
                    # A pre-invocation binding failure is known to have no
                    # effects.  An exception after entering a future component
                    # is conservatively unknown, never silently reported zero.
                    "providerCalls": None if component_invoked else 0,
                    "networkUsed": None if component_invoked else False,
                    "publicationAttempted": None if component_invoked else False,
                    "failure": {
                        "class": type(exc).__name__,
                        "summary": str(exc)[:1000],
                    },
                }
            )
        record["durationMs"] = max(0, (clock_ns() - started) // 1_000_000)
        record["componentDigest"] = _object_digest(record)
        component_records.append(record)
    duration_ms = max(0, (clock_ns() - suite_start) // 1_000_000)
    failed = [
        str(component["id"])
        for component in component_records
        if component["status"] != "passed"
    ]
    external_effects_known = all(
        component.get("providerCalls") is not None
        and component.get("networkUsed") is not None
        and component.get("publicationAttempted") is not None
        for component in component_records
    )
    authority = {
        "credentialInputsAccepted": [],
        "executionFlagsAccepted": [],
        "providerCalls": (
            sum(int(component["providerCalls"]) for component in component_records)
            if external_effects_known
            else None
        ),
        "networkUsed": (
            any(bool(component["networkUsed"]) for component in component_records)
            if external_effects_known
            else None
        ),
        "publicationAttempted": (
            any(
                bool(component["publicationAttempted"])
                for component in component_records
            )
            if external_effects_known
            else None
        ),
    }
    core: dict[str, object] = {
        "schemaVersion": 1,
        "suiteId": SUITE_ID,
        "mode": mode,
        "status": "passed" if not failed else "failed",
        "suiteManifest": {
            "path": manifest_relative,
            "digest": manifest_digest,
        },
        "authority": authority,
        "componentCount": len(component_records),
        "passedComponents": len(component_records) - len(failed),
        "failedComponents": failed,
        "components": component_records,
        "durationMs": duration_ms,
    }
    if (
        not external_effects_known
        or authority["providerCalls"] != 0
        or authority["networkUsed"] is not False
        or authority["publicationAttempted"] is not False
    ):
        core["status"] = "failed"
        if "suite-authority-boundary" not in failed:
            failed.append("suite-authority-boundary")
            core["failedComponents"] = failed
    summary = {**core, "summaryDigest": _object_digest(core)}
    (output / "summary.json").write_bytes(
        _pretty_json_bytes(summary, sort_keys=True)
    )
    (output / "summary.md").write_text(
        _render_markdown(summary), encoding="utf-8"
    )
    return summary


__all__ = [
    "COMPONENT_ORDER",
    "COMPONENT_RUNNERS",
    "DEFAULT_MANIFEST_PATH",
    "MODES",
    "SUITE_ID",
    "load_protocol_evaluation_suite_manifest",
    "run_provider_free_protocol_evaluation_suite",
]
