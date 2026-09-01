#!/usr/bin/env python3
"""Generate the deterministic provider-free Work Accounting V2 scale report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from math_flow.work_accounting_scale import (
    DEFAULT_INPUT_BUDGET_TOKENS,
    run_provider_free_work_accounting_scale_probe,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-budget-tokens",
        type=int,
        default=DEFAULT_INPUT_BUDGET_TOKENS,
        help="Nominal serialized-input threshold used by the bytes/4 estimate.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path; stdout is used when omitted.",
    )
    arguments = parser.parse_args()
    report = run_provider_free_work_accounting_scale_probe(
        input_budget_tokens=arguments.input_budget_tokens
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
