#!/usr/bin/env python3
"""Generate the deterministic inactive local-accounting-slice report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from math_flow.work_accounting_local_slice import (
    DEFAULT_MAX_BOUNDARY_NODES,
    DEFAULT_MAX_INCLUDED_NODES,
)
from math_flow.work_accounting_local_slice_probe import run_local_slice_probe


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-included-nodes",
        type=int,
        default=DEFAULT_MAX_INCLUDED_NODES,
    )
    parser.add_argument(
        "--max-boundary-nodes",
        type=int,
        default=DEFAULT_MAX_BOUNDARY_NODES,
    )
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    report = run_local_slice_probe(
        max_included_nodes=arguments.max_included_nodes,
        max_boundary_nodes=arguments.max_boundary_nodes,
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
