from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import MathFlowError
from .judges import project, render_request
from .repository import affected_problems, ledger, validate_pr, validate_tree
from .runs import run_judge_bundle
from .viewer import export_viewer_data


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

    affected_parser = commands.add_parser(
        "affected-problems", help="list problems affected between two Git commits"
    )
    affected_parser.add_argument("--base", required=True)
    affected_parser.add_argument("--head", default="HEAD")
    affected_parser.add_argument(
        "--global-pattern",
        action="append",
        default=[],
        help="path glob whose changes affect every problem (repeatable)",
    )

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

    run_parser = commands.add_parser("run", help="run a judge and write a protocol artifact bundle")
    run_parser.add_argument("--problem", required=True)
    run_parser.add_argument("--judge", required=True, type=Path)
    run_parser.add_argument("--head", default="HEAD", help="Git revision or WORKTREE")
    run_parser.add_argument("--output-dir", required=True, type=Path)
    run_parser.add_argument(
        "--base-run", type=Path, help="previous hierarchical judge-run bundle to update"
    )

    viewer_parser = commands.add_parser(
        "export-viewer", help="export a hierarchical run chain for the interactive viewer"
    )
    viewer_parser.add_argument("--problem", required=True)
    viewer_parser.add_argument("--head", default="HEAD")
    viewer_parser.add_argument(
        "--run-dir", required=True, action="append", type=Path, dest="run_dirs"
    )
    viewer_parser.add_argument("--output", required=True, type=Path)
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
        elif args.command == "affected-problems":
            result = affected_problems(
                root, args.base, args.head, args.global_pattern
            )
        elif args.command == "project":
            result = project(root, args.problem, args.judge, args.head)
            _write_json(result, args.output)
            return 0
        elif args.command == "render-request":
            result = render_request(root, args.problem, args.judge, args.head)
            _write_json(result, args.output)
            return 0
        elif args.command == "run":
            result = run_judge_bundle(
                root,
                args.problem,
                args.judge,
                args.head,
                args.output_dir,
                base_run=args.base_run,
            )
            _write_json(result, None)
            return 0
        elif args.command == "export-viewer":
            result = export_viewer_data(root, args.problem, args.head, args.run_dirs)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(args.output)
            return 0
        else:  # pragma: no cover
            raise AssertionError(args.command)
        _write_json(result, None)
        return 0
    except (MathFlowError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
