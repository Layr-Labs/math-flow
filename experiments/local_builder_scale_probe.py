#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from math_flow.builder_scale import run_provider_free_builder_context_scale_probe


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate valid synthetic knowledge states and compare V9 all-core "
            "context with bounded route/author packet models without a provider."
        )
    )
    parser.add_argument(
        "--input-budget-tokens",
        type=int,
        default=128_000,
        help="Nominal input budget used only for provider-free threshold reports.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New or replaceable JSON report path.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    report = run_provider_free_builder_context_scale_probe(
        input_budget_tokens=arguments.input_budget_tokens
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "providerCalls": report["providerCalls"],
                "cases": len(report["cases"]),
                "output": str(arguments.output),
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
