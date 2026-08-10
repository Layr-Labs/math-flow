from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .artifacts import verify_bundle
from .coordination import (
    claim_due_build,
    complete_build,
    fail_build,
    publish_batch,
    record_completed_inputs,
)
from .errors import MathFlowError
from .formation import run_knowledge_build_bundle
from .judgments import (
    detect_conflicts,
    load_judgment_bundle,
    run_primary_judgment_bundle,
    run_reconciliation_judgment_bundle,
)
from .judges import load_judge_spec, project, render_request
from .repository import affected_problems, ledger, sha256_json, validate_pr, validate_tree
from .runs import run_judge_bundle
from .viewer import export_viewer_catalog, export_viewer_data


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

    judgment_parser = commands.add_parser(
        "judgment", help="run one immutable parallel Markdown judgment"
    )
    judgment_parser.add_argument("--problem", required=True)
    judgment_parser.add_argument("--judge", required=True, type=Path)
    judgment_parser.add_argument("--head", default="HEAD")
    judgment_parser.add_argument(
        "--subject", required=True, action="append", dest="subjects",
        help="subject transaction ID (repeatable)",
    )
    judgment_parser.add_argument(
        "--evidence", action="append", default=[], dest="evidence",
        help="additional context transaction ID (repeatable)",
    )
    judgment_parser.add_argument("--output-dir", required=True, type=Path)

    conflict_parser = commands.add_parser(
        "detect-conflicts", help="derive reconciliation candidates from judgments"
    )
    conflict_parser.add_argument(
        "--judgment-dir", required=True, action="append", type=Path, dest="judgment_dirs"
    )
    conflict_parser.add_argument("--output", type=Path)

    reconcile_parser = commands.add_parser(
        "reconcile", help="run an immutable judgment over one detected conflict"
    )
    reconcile_parser.add_argument("--problem", required=True)
    reconcile_parser.add_argument("--judge", required=True, type=Path)
    reconcile_parser.add_argument("--head", default="HEAD")
    reconcile_parser.add_argument("--conflicts", required=True, type=Path)
    reconcile_parser.add_argument("--conflict-id", required=True)
    reconcile_parser.add_argument(
        "--judgment-dir", required=True, action="append", type=Path, dest="judgment_dirs"
    )
    reconcile_parser.add_argument("--output-dir", required=True, type=Path)

    trigger_parser = commands.add_parser(
        "knowledge-trigger", help="mark a rate-limited knowledge-build lane dirty"
    )
    trigger_parser.add_argument("--scheduler-file", required=True, type=Path)
    trigger_parser.add_argument("--problem", required=True)
    builder_identity = trigger_parser.add_mutually_exclusive_group(required=True)
    builder_identity.add_argument("--builder-digest")
    builder_identity.add_argument("--builder", type=Path)
    trigger_parser.add_argument("--minimum-interval", required=True, type=int)
    trigger_parser.add_argument(
        "--judgment-dir", action="append", default=[], type=Path, dest="judgment_dirs"
    )
    trigger_parser.add_argument("--conflicts", type=Path)
    trigger_parser.add_argument("--now", type=int)
    trigger_parser.add_argument("--output", type=Path)

    claim_parser = commands.add_parser(
        "knowledge-claim", help="claim an eligible coalesced knowledge build"
    )
    claim_parser.add_argument("--scheduler-file", required=True, type=Path)
    claim_parser.add_argument("--lane-id", required=True)
    claim_parser.add_argument("--maximum-judgments", type=int, default=500)
    claim_parser.add_argument("--now", type=int)
    claim_parser.add_argument("--output", type=Path)

    formation_parser = commands.add_parser(
        "knowledge-build", help="materialize one claimed judgment batch into knowledge state"
    )
    formation_parser.add_argument("--problem", required=True)
    formation_parser.add_argument("--builder", required=True, type=Path)
    formation_parser.add_argument("--head", default="HEAD")
    formation_parser.add_argument("--claim", required=True, type=Path)
    formation_parser.add_argument(
        "--judgment-dir", action="append", default=[], type=Path, dest="judgment_dirs"
    )
    formation_parser.add_argument("--conflicts", type=Path)
    formation_parser.add_argument("--base-run", type=Path)
    formation_parser.add_argument("--checkpoint-dir", type=Path)
    formation_parser.add_argument("--output-dir", required=True, type=Path)

    complete_parser = commands.add_parser(
        "knowledge-complete", help="advance a knowledge lane after a successful build"
    )
    complete_parser.add_argument("--scheduler-file", required=True, type=Path)
    complete_parser.add_argument("--lane-id", required=True)
    complete_parser.add_argument("--build-token", required=True)
    complete_source = complete_parser.add_mutually_exclusive_group(required=True)
    complete_source.add_argument("--state-run-digest")
    complete_source.add_argument("--state-run-dir", type=Path)
    complete_parser.add_argument("--now", type=int)

    fail_parser = commands.add_parser(
        "knowledge-fail", help="return a failed knowledge build to its lane"
    )
    fail_parser.add_argument("--scheduler-file", required=True, type=Path)
    fail_parser.add_argument("--lane-id", required=True)
    fail_parser.add_argument("--build-token", required=True)
    fail_parser.add_argument("--now", type=int)

    publish_parser = commands.add_parser(
        "publish-batch", help="stage verified run bundles in a projection worktree"
    )
    publish_parser.add_argument("--projection-dir", required=True, type=Path)
    publish_parser.add_argument(
        "--bundle", required=True, action="append", type=Path, dest="bundles"
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

    catalog_parser = commands.add_parser(
        "export-viewer-catalog",
        help="export published projection-branch state for the repository viewer",
    )
    catalog_parser.add_argument("--projection-dir", required=True, type=Path)
    catalog_parser.add_argument("--repository", required=True, help="GitHub owner/repository slug")
    catalog_parser.add_argument("--canonical-ref", default="main")
    catalog_parser.add_argument("--projection-ref", default="projections")
    catalog_parser.add_argument("--output", required=True, type=Path)
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
        elif args.command == "judgment":
            result = run_primary_judgment_bundle(
                root,
                args.problem,
                args.judge,
                args.head,
                args.subjects,
                args.output_dir,
                context_transaction_ids=args.evidence,
            )
        elif args.command == "detect-conflicts":
            result = {"schemaVersion": 1, "conflicts": detect_conflicts(args.judgment_dirs)}
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "reconcile":
            value = json.loads(args.conflicts.read_text(encoding="utf-8"))
            records = value.get("conflicts") if isinstance(value, dict) else None
            if not isinstance(records, list):
                raise MathFlowError("conflict input must contain a conflicts array")
            matches = [
                record
                for record in records
                if isinstance(record, dict) and record.get("conflictId") == args.conflict_id
            ]
            if len(matches) != 1:
                raise MathFlowError("requested conflict ID is not unique in the conflict input")
            result = run_reconciliation_judgment_bundle(
                root,
                args.problem,
                args.judge,
                args.head,
                matches[0],
                args.judgment_dirs,
                args.output_dir,
            )
        elif args.command == "knowledge-trigger":
            builder_digest = (
                f"sha256:{sha256_json(load_judge_spec(args.builder))}"
                if args.builder
                else args.builder_digest
            )
            judgment_ids = []
            for bundle_dir in args.judgment_dirs:
                _, judgment, _ = load_judgment_bundle(bundle_dir)
                if judgment.get("problemId") != args.problem:
                    raise MathFlowError("knowledge trigger judgment belongs to another problem")
                judgment_ids.append(str(judgment["judgmentId"]))
            conflict_ids = []
            if args.conflicts:
                value = json.loads(args.conflicts.read_text(encoding="utf-8"))
                records = value.get("conflicts") if isinstance(value, dict) else None
                if not isinstance(records, list):
                    raise MathFlowError("conflict input must contain a conflicts array")
                for record in records:
                    if not isinstance(record, dict) or record.get("problemId") != args.problem:
                        raise MathFlowError("knowledge trigger conflict belongs to another problem")
                    conflict_ids.append(str(record.get("conflictId")))
            result = record_completed_inputs(
                args.scheduler_file,
                args.problem,
                builder_digest,
                judgment_ids,
                conflict_ids,
                args.minimum_interval,
                args.now if args.now is not None else int(time.time()),
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "knowledge-claim":
            result = claim_due_build(
                args.scheduler_file,
                args.lane_id,
                args.now if args.now is not None else int(time.time()),
                args.maximum_judgments,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "knowledge-build":
            claim = json.loads(args.claim.read_text(encoding="utf-8"))
            result = run_knowledge_build_bundle(
                root,
                args.problem,
                args.builder,
                args.head,
                claim,
                args.judgment_dirs,
                args.conflicts,
                args.output_dir,
                base_run=args.base_run,
                checkpoint_dir=args.checkpoint_dir,
            )
        elif args.command == "knowledge-complete":
            if args.state_run_dir:
                manifest, state_run_digest = verify_bundle(args.state_run_dir)
                if manifest.get("runKind") != "knowledge-build":
                    raise MathFlowError("knowledge completion bundle is not a knowledge build")
            else:
                state_run_digest = args.state_run_digest
            result = complete_build(
                args.scheduler_file,
                args.lane_id,
                args.build_token,
                state_run_digest,
                args.now if args.now is not None else int(time.time()),
            )
        elif args.command == "knowledge-fail":
            result = fail_build(
                args.scheduler_file,
                args.lane_id,
                args.build_token,
                args.now if args.now is not None else int(time.time()),
            )
        elif args.command == "publish-batch":
            result = publish_batch(args.projection_dir, args.bundles)
        elif args.command == "export-viewer":
            result = export_viewer_data(root, args.problem, args.head, args.run_dirs)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(args.output)
            return 0
        elif args.command == "export-viewer-catalog":
            result = export_viewer_catalog(
                root,
                args.projection_dir,
                args.repository,
                canonical_ref=args.canonical_ref,
                projection_ref=args.projection_ref,
            )
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
    except (MathFlowError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
