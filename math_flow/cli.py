from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import MathFlowError
from .judges import project, render_request
from .repository import ledger, validate_pr, validate_tree


def _write_json(value: object, output: str | None) -> None:
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(target)
    else:
        print(rendered, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="math-flow", description="Validate and replay the Math Flow protocol")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("validate-tree", help="validate all problem and contribution folders")

    validate_pr_parser = commands.add_parser("validate-pr", help="validate one contribution-only PR diff")
    validate_pr_parser.add_argument("--base", required=True, help="base commit or revision")
    validate_pr_parser.add_argument("--head", required=True, help="head commit or revision")

    ledger_parser = commands.add_parser("ledger", help="derive a problem ledger from first-parent Git history")
    ledger_parser.add_argument("--problem", required=True)
    ledger_parser.add_argument("--head", default="HEAD")

    project_parser = commands.add_parser("project", help="run a versioned judge over a ledger prefix")
    project_parser.add_argument("--problem", required=True)
    project_parser.add_argument("--judge", required=True, type=Path)
    project_parser.add_argument("--head", default="HEAD", help="Git revision or WORKTREE for local preview")
    project_parser.add_argument("--output", help="write JSON to this path instead of stdout")

    request_parser = commands.add_parser(
        "render-request", help="render an OpenRouter request without sending it"
    )
    request_parser.add_argument("--problem", required=True)
    request_parser.add_argument("--judge", required=True, type=Path)
    request_parser.add_argument("--head", default="HEAD", help="Git revision or WORKTREE")
    request_parser.add_argument("--output", help="write JSON to this path instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    try:
        if args.command == "validate-tree":
            result = validate_tree(root)
        elif args.command == "validate-pr":
            result = validate_pr(root, args.base, args.head)
        elif args.command == "ledger":
            result = ledger(root, args.problem, args.head)
        elif args.command == "project":
            result = project(root, args.problem, args.judge, args.head)
            _write_json(result, args.output)
            return 0
        elif args.command == "render-request":
            result = render_request(root, args.problem, args.judge, args.head)
            _write_json(result, args.output)
            return 0
        else:  # pragma: no cover
            raise AssertionError(args.command)
        _write_json(result, None)
        return 0
    except (MathFlowError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
