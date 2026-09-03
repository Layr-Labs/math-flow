"""Plan or explicitly execute the unpublished BSSC joint K1->K3 holdout."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_serial_hosted import (
    DEFAULT_MANIFEST,
    build_joint_hosted_plan,
    load_joint_hosted_manifest,
    run_joint_hosted_holdout,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _new_directory(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.exists():
        raise MathFlowError(
            "joint hosted-runner output directory already exists; "
            "refusing stale artifact reuse"
        )
    resolved.mkdir(parents=True)
    return resolved


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a zero-call plan by default, or explicitly execute one fresh, "
            "publication-forbidden BSSC joint K1-K3 semantic holdout."
        )
    )
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--manifest", type=Path, default=Path(DEFAULT_MANIFEST))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--execute-provider",
        action="store_true",
        help="Enable the provider only with the manifest-bound environment authorization.",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    manifest = load_joint_hosted_manifest(args.manifest, repository_root=root)
    output = _new_directory(args.output_dir)
    _write_json(output / "manifest.json", manifest)
    _write_json(output / "plan.json", build_joint_hosted_plan(manifest))
    if not args.execute_provider:
        print(
            json.dumps(
                {
                    "status": "planned",
                    "providerCalls": 0,
                    "publicationAttempted": False,
                    "outputDir": str(output),
                }
            )
        )
        return 0

    variable = str(manifest["authorizationEnvironmentVariable"])
    authorization = os.environ.get(variable, "")
    if authorization != manifest["authorizationValue"]:
        raise MathFlowError(f"provider execution requires exact {variable} authorization")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise MathFlowError("OPENROUTER_API_KEY is required for provider execution")
    report = run_joint_hosted_holdout(
        repository_root=root,
        manifest=manifest,
        bundle_dir=output / "bundle",
        checkpoint_dir=output / "checkpoints",
        authorization=authorization,
    )
    _write_json(output / "report.json", report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "providerCalls": report["telemetry"]["providerCalls"],
                "reportedCostUsd": report["telemetry"]["reportedCostUsd"],
                "publicationAttempted": False,
                "outputDir": str(output),
            }
        )
    )
    return 0 if report["status"] == "completed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MathFlowError as exc:
        raise SystemExit(str(exc)) from exc
