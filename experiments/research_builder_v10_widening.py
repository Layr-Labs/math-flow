"""Plan or explicitly run the unpublished Builder V10 route/refine suite."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.openrouter import send_chat_completion
from math_flow.research_builder_v10_widening import (
    load_bound_widening_spec,
    load_widening_manifest,
    plan_widening_experiment,
    run_widening_experiment,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPOSITORY_ROOT
    / "protocol/experiments/local-builder-v10-widening-v1/manifest.json"
)


def _new_output_directory(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.exists():
        raise MathFlowError(
            "V10 widening output directory already exists; refusing stale artifact reuse"
        )
    resolved.mkdir(parents=True)
    return resolved


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a provider-free plan by default, or explicitly run the "
            "publication-forbidden Builder V10 route/refine widening suite."
        )
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--execute-provider",
        action="store_true",
        help="Enable calls only after the manifest-named authorization is also set.",
    )
    args = parser.parse_args(argv)
    manifest = load_widening_manifest(
        args.manifest, repository_root=REPOSITORY_ROOT
    )
    spec = load_bound_widening_spec(manifest, repository_root=REPOSITORY_ROOT)
    if args.execute_provider:
        variable = str(manifest["authorizationEnvironmentVariable"])
        expected = str(manifest["authorizationValue"])
        if os.environ.get(variable) != expected:
            raise MathFlowError(
                f"provider execution requires exact {variable} authorization"
            )
    output_dir = _new_output_directory(args.output_dir)
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "candidate-judge-spec.json", spec)
    if not args.execute_provider:
        report = plan_widening_experiment(manifest, spec=spec)
        _write_json(output_dir / "plan.json", report)
        print(json.dumps({"status": "planned", "outputDir": str(output_dir)}))
        return 0

    report = run_widening_experiment(
        manifest,
        spec=spec,
        transport=send_chat_completion,
    )
    _write_json(output_dir / "report.json", report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "outputDir": str(output_dir),
                "providerCalls": report["telemetry"]["providerCalls"],
                "publicationAttempted": False,
            }
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MathFlowError as exc:
        raise SystemExit(str(exc)) from exc
