from __future__ import annotations

from pathlib import Path

from . import __version__
from .artifacts import ArtifactBundle
from .errors import MathFlowError
from .hierarchical import run_hierarchical_judge
from .judges import load_judge_spec, load_source, project
from .openrouter import OpenRouterTransport
from .repository import sha256_json


def _envelope(
    problem: str,
    source: dict[str, object],
    spec: dict[str, object],
    base_run: str | None,
    request_digests: list[str],
    provider_runs: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "protocolVersion": 1,
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "judgeSpec": {"id": spec["id"], "digest": f"sha256:{sha256_json(spec)}"},
        "runner": {
            "implementation": spec["implementation"],
            "mathFlowVersion": __version__,
        },
        "judgeBuilder": {
            "inputBuilder": spec["inputBuilder"],
            "invocationAdapter": spec["invocationAdapter"],
            "outputAdapter": spec["outputAdapter"],
            "reducer": spec["reducer"],
        },
        "baseRun": base_run,
        "outputProfile": spec["outputProfile"],
        "requestDigests": request_digests,
        "providerRuns": provider_runs,
    }


def run_judge_bundle(
    root: Path,
    problem: str,
    judge_path: Path,
    head: str,
    output_dir: Path,
    base_run: Path | None = None,
    transport: OpenRouterTransport | None = None,
) -> dict[str, object]:
    root = root.resolve()
    spec = load_judge_spec(judge_path)
    source = load_source(root, problem, head)
    bundle = ArtifactBundle(output_dir)

    if spec["implementation"] == "openrouter-hierarchical-markdown-v1":
        result = run_hierarchical_judge(
            root, problem, spec, source, head, base_run, transport=transport
        )
        bundle.add_json("control/selection.json", result["selection"], "node-selection")
        bundle.add_text("report.md", result["report"], "report", "text/markdown")
        bundle.add_json("state/delta.json", result["delta"], "knowledge-delta")
        bundle.add_json("state/state.json", result["state"], "knowledge-state")
        envelope = _envelope(
            problem,
            source,
            spec,
            result["baseRunDigest"],
            result["requestDigests"],
            result["providerRuns"],
        )
        return bundle.finalize(envelope)

    if base_run is not None:
        raise MathFlowError("flat projection profiles do not accept a base judge run")
    projection = project(root, problem, judge_path, head, transport=transport)
    bundle.add_json("projection.json", projection, "flat-projection")
    request_digest = projection.get("judgeRequestDigest")
    provider_run = projection.get("providerRun")
    envelope = _envelope(
        problem,
        source,
        spec,
        None,
        [request_digest] if isinstance(request_digest, str) else [],
        [provider_run] if isinstance(provider_run, dict) else [],
    )
    return bundle.finalize(envelope)
