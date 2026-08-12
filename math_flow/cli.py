from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from .artifacts import verify_bundle
from .attestations import (
    load_verifier_spec,
    plan_verifier_attestation,
    run_verifier_attestation_bundle,
    verifier_spec_digest,
    verify_verifier_attestation_bundle,
)
from .coordination import (
    claim_due_build,
    complete_build,
    fail_build,
    publish_batch,
    record_completed_inputs,
)
from .context import materialize_agent_context
from .credit import run_credit_assignment_bundle
from .credit_schedule import (
    filter_credit_dispatch_history,
    plan_credit_run,
    plan_due_credit_dispatches,
)
from .directions import research_direction_ledger
from .discovery import discover_problems
from .errors import MathFlowError
from .formation import run_knowledge_build_bundle
from .governance import (
    list_active_projections,
    resolve_projection,
    validate_admission_pr,
    validate_projection_registry,
)
from .github_projection import publish_github_projection
from .judgments import (
    detect_conflicts,
    load_judgment_bundle,
    plan_primary_judgment_inputs,
    plan_primary_judgment_coverage,
    plan_reconciliation_inputs,
    run_primary_judgment_bundle,
    run_reconciliation_judgment_bundle,
    verify_primary_judgment_artifacts,
)
from .judges import load_judge_spec, project, render_request
from .projection_dependencies import resolve_projection_dependencies
from .projection_queue import (
    filter_projection_dispatch_history,
    merge_scheduler_states,
    plan_due_projection_dispatches,
)
from .repository import affected_problems, ledger, sha256_json, validate_pr, validate_tree
from .runs import run_judge_bundle
from .scale_probe import run_provider_free_scale_probe
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

    commands.add_parser(
        "validate-tree",
        help="validate all problem, contribution, and research-direction folders",
    )

    commands.add_parser(
        "validate-projections", help="validate the approved projection registry"
    )

    verifier_digest_parser = commands.add_parser(
        "verifier-spec-digest",
        help="validate a verifier spec and print its canonical content digest",
    )
    verifier_digest_parser.add_argument("--verifier", required=True, type=Path)

    resolve_projection_parser = commands.add_parser(
        "resolve-projection",
        help="resolve one approved projection for a problem at a Git commit",
    )
    resolve_projection_parser.add_argument("--projection", required=True)
    resolve_projection_parser.add_argument("--problem", required=True)
    resolve_projection_parser.add_argument("--head", default="HEAD")
    resolve_projection_parser.add_argument("--output")

    dependency_parser = commands.add_parser(
        "resolve-projection-dependencies",
        help="lock a projection's governed dependencies to verified published runs",
    )
    dependency_parser.add_argument("--projection", required=True)
    dependency_parser.add_argument("--problem", required=True)
    dependency_parser.add_argument("--head", default="HEAD")
    dependency_parser.add_argument(
        "--projection-dir", required=True, type=Path
    )
    dependency_parser.add_argument("--output")

    credit_parser = commands.add_parser(
        "credit",
        help="run a governed credit overlay over its locked projection dependencies",
    )
    credit_parser.add_argument("--projection", required=True)
    credit_parser.add_argument("--problem", required=True)
    credit_parser.add_argument("--head", default="HEAD")
    credit_parser.add_argument(
        "--projection-dir", required=True, type=Path
    )
    credit_parser.add_argument("--output-dir", required=True, type=Path)
    credit_parser.add_argument(
        "--as-of",
        type=int,
        help="eligibility evaluation epoch (default: current time)",
    )

    credit_plan_parser = commands.add_parser(
        "credit-plan",
        help="plan governed credit eligibility without calling a provider",
    )
    credit_plan_parser.add_argument("--projection", required=True)
    credit_plan_parser.add_argument("--problem", required=True)
    credit_plan_parser.add_argument("--head", default="HEAD")
    credit_plan_parser.add_argument("--projection-dir", required=True, type=Path)
    credit_plan_parser.add_argument("--as-of", type=int)
    credit_plan_parser.add_argument("--output")

    due_credit_parser = commands.add_parser(
        "due-credit-plan",
        help="plan all eligible governed credit overlay dispatches",
    )
    due_credit_parser.add_argument("--projection-dir", required=True, type=Path)
    due_credit_parser.add_argument("--head", default="HEAD")
    due_credit_parser.add_argument("--as-of", type=int)
    due_credit_parser.add_argument("--output")

    filter_credit_parser = commands.add_parser(
        "filter-credit-plan",
        help="suppress active or repeatedly failing automatic credit retries",
    )
    filter_credit_parser.add_argument("--plan", required=True, type=Path)
    filter_credit_parser.add_argument("--run-history", required=True, type=Path)
    filter_credit_parser.add_argument("--output", required=True)

    active_projections_parser = commands.add_parser(
        "list-active-projections",
        help="list approved active projections for one problem at a Git commit",
    )
    active_projections_parser.add_argument("--problem", required=True)
    active_projections_parser.add_argument("--head", default="HEAD")
    active_projections_parser.add_argument(
        "--engine", help="only list projections executed by this engine"
    )
    active_projections_parser.add_argument("--output")

    problems_parser = commands.add_parser(
        "list-problems",
        help="list all canonical problems and their contribution/projection stage",
    )
    problems_parser.add_argument("--head", default="HEAD")
    problems_parser.add_argument(
        "--projection-dir",
        type=Path,
        help="verify and annotate published knowledge state from this projection checkout",
    )
    problems_parser.add_argument(
        "--stage",
        action="append",
        choices=[
            "ready-for-first-contribution",
            "projection-unchecked",
            "knowledge-pending",
            "knowledge-stale",
            "knowledge-current",
        ],
        help="only return this lifecycle stage (repeatable)",
    )
    problems_parser.add_argument("--output")

    admission_parser = commands.add_parser(
        "validate-admission-pr",
        help="validate a problem/projection admission and its admin approvals",
    )
    admission_parser.add_argument("--base", required=True)
    admission_parser.add_argument("--head", required=True)
    admission_parser.add_argument(
        "--approver",
        action="append",
        default=[],
        help="GitHub login with a current-head approving review (repeatable)",
    )
    admission_parser.add_argument(
        "--approval-comments",
        type=Path,
        help="JSON array of current PR comments normalized to author and body",
    )

    validate_pr_parser = commands.add_parser(
        "validate-pr", help="validate one atomic contribution or direction-event PR diff"
    )
    validate_pr_parser.add_argument("--base", required=True, help="base commit or revision")
    validate_pr_parser.add_argument("--head", required=True, help="head commit or revision")

    ledger_parser = commands.add_parser("ledger", help="derive a problem ledger from first-parent Git history")
    ledger_parser.add_argument("--problem", required=True)
    ledger_parser.add_argument("--head", default="HEAD")

    directions_parser = commands.add_parser(
        "directions",
        help="derive canonical research-direction events and current statuses",
    )
    directions_parser.add_argument("--problem", required=True)
    directions_parser.add_argument("--head", default="HEAD")
    directions_parser.add_argument(
        "--status", choices=["active", "released", "completed"]
    )
    directions_parser.add_argument("--output")

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

    attest_parser = commands.add_parser(
        "attest",
        help="execute a contribution's pinned OCI verifier and write an attestation bundle",
    )
    attest_parser.add_argument("--problem", required=True)
    attest_parser.add_argument(
        "--transaction", required=True, help="canonical contribution transaction commit"
    )
    attest_parser.add_argument(
        "--head", default="HEAD", help="canonical ledger head containing the transaction"
    )
    attest_parser.add_argument("--output-dir", required=True, type=Path)

    attestation_plan_parser = commands.add_parser(
        "attestation-plan",
        help="plan one canonical objective-verification request without executing it",
    )
    attestation_plan_parser.add_argument("--problem", required=True)
    attestation_plan_parser.add_argument("--transaction", required=True)
    attestation_plan_parser.add_argument("--head", default="HEAD")
    attestation_plan_parser.add_argument("--projection-dir", required=True, type=Path)
    attestation_plan_parser.add_argument("--output", type=Path)

    verify_attestation_parser = commands.add_parser(
        "verify-attestation",
        help="verify a durable verifier attestation and optionally replay its OCI command",
    )
    verify_attestation_parser.add_argument("--bundle", required=True, type=Path)
    verify_attestation_parser.add_argument(
        "--head", default="HEAD", help="current canonical head used for stale-subject checks"
    )
    verify_attestation_parser.add_argument(
        "--replay", action="store_true", help="rerun the pinned OCI verifier and compare bytes"
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

    judgment_plan_parser = commands.add_parser(
        "judgment-plan",
        help="find transactions missing a published primary judgment from one judge",
    )
    judgment_plan_parser.add_argument("--problem", required=True)
    judgment_plan_parser.add_argument("--judge", required=True, type=Path)
    judgment_plan_parser.add_argument("--head", default="HEAD")
    judgment_plan_parser.add_argument("--projection-dir", required=True, type=Path)
    judgment_plan_parser.add_argument("--output", type=Path)

    judgment_input_parser = commands.add_parser(
        "judgment-input-plan",
        help="combine verified published and newly produced primary judgments",
    )
    judgment_input_parser.add_argument("--problem", required=True)
    judgment_input_parser.add_argument("--judge", required=True, type=Path)
    judgment_input_parser.add_argument("--head", default="HEAD")
    judgment_input_parser.add_argument("--projection-dir", required=True, type=Path)
    judgment_input_parser.add_argument(
        "--additional-root",
        action="append",
        default=[],
        type=Path,
        dest="additional_roots",
    )
    judgment_input_parser.add_argument(
        "--expected-new-subject",
        action="append",
        default=[],
        dest="expected_new_subjects",
    )
    judgment_input_parser.add_argument("--output", type=Path)

    reconciliation_plan_parser = commands.add_parser(
        "reconciliation-plan",
        help="derive current conflicts and bind published/new reconciliations",
    )
    reconciliation_plan_parser.add_argument("--problem", required=True)
    reconciliation_plan_parser.add_argument(
        "--primary-judge", required=True, type=Path
    )
    reconciliation_plan_parser.add_argument(
        "--reconciliation-judge", required=True, type=Path
    )
    reconciliation_plan_parser.add_argument("--head", default="HEAD")
    reconciliation_plan_parser.add_argument(
        "--projection-dir", required=True, type=Path
    )
    reconciliation_plan_parser.add_argument(
        "--primary-judgment-dir",
        action="append",
        default=[],
        type=Path,
        dest="primary_judgment_dirs",
    )
    reconciliation_plan_parser.add_argument(
        "--additional-root",
        action="append",
        default=[],
        type=Path,
        dest="reconciliation_additional_roots",
    )
    reconciliation_plan_parser.add_argument(
        "--expected-new-conflict",
        action="append",
        default=None,
        dest="expected_new_conflicts",
    )
    reconciliation_plan_parser.add_argument("--output", type=Path)

    verify_judgments_parser = commands.add_parser(
        "verify-judgment-artifacts",
        help="discover and verify downloaded primary-judgment bundles",
    )
    verify_judgments_parser.add_argument("--problem", required=True)
    verify_judgments_parser.add_argument("--judge", required=True, type=Path)
    verify_judgments_parser.add_argument("--head", default="HEAD")
    verify_judgments_parser.add_argument("--search-root", required=True, type=Path)
    verify_judgments_parser.add_argument(
        "--expected-subject",
        action="append",
        default=[],
        dest="expected_subjects",
    )
    verify_judgments_parser.add_argument("--output", type=Path)

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
    trigger_parser.add_argument("--head", default="HEAD")
    builder_identity = trigger_parser.add_mutually_exclusive_group(required=True)
    builder_identity.add_argument("--builder-digest")
    builder_identity.add_argument("--builder", type=Path)
    trigger_parser.add_argument(
        "--projection-digest",
        help="approved projection-spec digest used to isolate this logical lane",
    )
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
    fail_parser.add_argument("--problem-ledger-digest")
    fail_parser.add_argument("--now", type=int)

    publish_parser = commands.add_parser(
        "publish-batch", help="stage verified run bundles in a projection worktree"
    )
    publish_parser.add_argument("--projection-dir", required=True, type=Path)
    publish_parser.add_argument(
        "--bundle", required=True, action="append", type=Path, dest="bundles"
    )

    github_publish_parser = commands.add_parser(
        "github-publish-projection",
        help="atomically publish projection changes as a GitHub-signed commit",
    )
    github_publish_parser.add_argument("--projection-dir", required=True, type=Path)
    github_publish_parser.add_argument("--repository", required=True)
    github_publish_parser.add_argument("--branch", default="projections")
    github_publish_parser.add_argument("--message", required=True)

    merge_scheduler_parser = commands.add_parser(
        "merge-schedulers",
        help="three-way merge disjoint knowledge-scheduler lane updates",
    )
    merge_scheduler_parser.add_argument("--base", required=True, type=Path)
    merge_scheduler_parser.add_argument("--ours", required=True, type=Path)
    merge_scheduler_parser.add_argument("--theirs", required=True, type=Path)
    merge_scheduler_parser.add_argument("--output", required=True, type=Path)

    due_projection_parser = commands.add_parser(
        "due-projection-plan",
        help="plan governed projection dispatches for eligible knowledge lanes",
    )
    due_projection_parser.add_argument("--scheduler-file", required=True, type=Path)
    due_projection_parser.add_argument(
        "--projection-dir",
        type=Path,
        help="published projection root used to recover missing or stale lanes",
    )
    due_projection_parser.add_argument("--head", default="HEAD")
    due_projection_parser.add_argument("--now", type=int)
    due_projection_parser.add_argument("--output", type=Path)

    filter_projection_parser = commands.add_parser(
        "filter-projection-plan",
        help="suppress duplicate or repeatedly failing same-head projection runs",
    )
    filter_projection_parser.add_argument("--plan", required=True, type=Path)
    filter_projection_parser.add_argument(
        "--run-history", required=True, type=Path
    )
    filter_projection_parser.add_argument("--output", required=True, type=Path)

    viewer_parser = commands.add_parser(
        "export-viewer", help="export a hierarchical run chain for the interactive viewer"
    )
    viewer_parser.add_argument("--problem", required=True)
    viewer_parser.add_argument("--head", default="HEAD")
    viewer_parser.add_argument(
        "--run-dir", required=True, action="append", type=Path, dest="run_dirs"
    )
    viewer_parser.add_argument(
        "--judgment-dir", action="append", type=Path, dest="judgment_dirs"
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

    context_parser = commands.add_parser(
        "context",
        help="materialize a verified latest knowledge state for a non-UI agent",
    )
    context_parser.add_argument("--problem", required=True)
    context_parser.add_argument(
        "--projection-dir",
        required=True,
        type=Path,
        help="local worktree containing the published projection branch",
    )
    context_parser.add_argument(
        "--projection",
        help="projection ID; required when the problem has multiple projections",
    )
    context_parser.add_argument(
        "--credit-projection",
        help=(
            "qualitative credit projection ID; when omitted, the sole applicable "
            "credit projection is selected and multiple choices are reported in context.json"
        ),
    )
    context_parser.add_argument("--head", default="HEAD", help="canonical Git revision")
    context_parser.add_argument(
        "--node",
        action="append",
        default=[],
        dest="nodes",
        help="limit context.md to this node and its descendants (repeatable)",
    )
    context_parser.add_argument("--output-dir", required=True, type=Path)

    scale_parser = commands.add_parser(
        "provider-free-scale-probe",
        help="stress scheduling, publication, viewer, and context isolation without model calls",
    )
    scale_parser.add_argument("--problems", type=int, default=12)
    scale_parser.add_argument("--projections-per-problem", type=int, default=4)
    scale_parser.add_argument("--solvers", type=int, default=12)
    scale_parser.add_argument("--minimum-interval", type=int, default=300)
    scale_parser.add_argument("--maximum-judgments", type=int, default=64)
    scale_parser.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    try:
        if args.command == "validate-tree":
            result = validate_tree(root)
        elif args.command == "provider-free-scale-probe":
            result = run_provider_free_scale_probe(
                problems=args.problems,
                projections=args.projections_per_problem,
                solvers=args.solvers,
                minimum_interval_seconds=args.minimum_interval,
                maximum_judgments_per_build=args.maximum_judgments,
            )
            _write_json(result, args.output)
            return 0
        elif args.command == "validate-projections":
            result = validate_projection_registry(root)
        elif args.command == "verifier-spec-digest":
            spec = load_verifier_spec(args.verifier)
            result = {"id": spec["id"], "digest": verifier_spec_digest(spec)}
        elif args.command == "resolve-projection":
            result = resolve_projection(
                root, args.projection, args.problem, args.head
            )
            _write_json(result, args.output)
            return 0
        elif args.command == "resolve-projection-dependencies":
            result = resolve_projection_dependencies(
                root,
                args.projection_dir,
                args.projection,
                args.problem,
                args.head,
            )
            _write_json(result, args.output)
            return 0
        elif args.command == "credit":
            result = run_credit_assignment_bundle(
                root,
                args.projection_dir,
                args.projection,
                args.problem,
                args.head,
                args.output_dir,
                as_of=args.as_of,
            )
        elif args.command == "credit-plan":
            result = plan_credit_run(
                root,
                args.projection_dir,
                args.projection,
                args.problem,
                args.head,
                args.as_of,
            )
            _write_json(result, args.output)
            return 0
        elif args.command == "due-credit-plan":
            result = plan_due_credit_dispatches(
                root, args.projection_dir, args.head, args.as_of
            )
            _write_json(result, args.output)
            return 0
        elif args.command == "filter-credit-plan":
            try:
                plan = json.loads(args.plan.read_text(encoding="utf-8"))
                run_history = json.loads(
                    args.run_history.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError) as exc:
                raise MathFlowError(
                    f"could not read credit dispatch history inputs: {exc}"
                ) from exc
            result = filter_credit_dispatch_history(plan, run_history)
            _write_json(result, args.output)
            return 0
        elif args.command == "list-active-projections":
            result = list_active_projections(
                root, args.problem, args.head, args.engine
            )
            _write_json(result, args.output)
            return 0
        elif args.command == "list-problems":
            result = discover_problems(root, args.head, args.projection_dir)
            if args.stage:
                stages = set(args.stage)
                result = {
                    **result,
                    "problems": [
                        item for item in result["problems"] if item["stage"] in stages
                    ],
                }
            _write_json(result, args.output)
            return 0
        elif args.command == "validate-admission-pr":
            approval_comments = None
            if args.approval_comments is not None:
                try:
                    approval_comments = json.loads(
                        args.approval_comments.read_text(encoding="utf-8")
                    )
                except (OSError, json.JSONDecodeError) as exc:
                    raise MathFlowError(
                        f"could not read admission approval comments: {exc}"
                    ) from exc
            result = validate_admission_pr(
                root,
                args.base,
                args.head,
                args.approver,
                approval_comments,
            )
        elif args.command == "validate-pr":
            result = validate_pr(root, args.base, args.head)
        elif args.command == "ledger":
            result = ledger(root, args.problem, args.head)
        elif args.command == "directions":
            result = research_direction_ledger(root, args.problem, args.head)
            if args.status is not None:
                result = {
                    **result,
                    "directions": [
                        item
                        for item in result["directions"]
                        if item["status"] == args.status
                    ],
                }
            _write_json(result, args.output)
            return 0
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
        elif args.command == "attest":
            result = run_verifier_attestation_bundle(
                root,
                args.problem,
                args.transaction,
                args.head,
                args.output_dir,
            )
        elif args.command == "attestation-plan":
            result = plan_verifier_attestation(
                root,
                args.projection_dir,
                args.problem,
                args.transaction,
                args.head,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "verify-attestation":
            result = verify_verifier_attestation_bundle(
                root,
                args.bundle,
                args.head,
                replay=args.replay,
            )
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
        elif args.command == "judgment-plan":
            result = plan_primary_judgment_coverage(
                root,
                args.projection_dir,
                args.problem,
                args.judge,
                args.head,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "judgment-input-plan":
            result = plan_primary_judgment_inputs(
                root,
                args.projection_dir,
                args.problem,
                args.judge,
                args.head,
                args.additional_roots,
                args.expected_new_subjects,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "reconciliation-plan":
            result = plan_reconciliation_inputs(
                root,
                args.projection_dir,
                args.problem,
                args.primary_judge,
                args.reconciliation_judge,
                args.head,
                args.primary_judgment_dirs,
                args.reconciliation_additional_roots,
                args.expected_new_conflicts,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "verify-judgment-artifacts":
            result = verify_primary_judgment_artifacts(
                root,
                args.search_root,
                args.problem,
                args.judge,
                args.head,
                args.expected_subjects,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
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
            reconciliation_dependencies: dict[str, dict[str, object]] = {}
            for bundle_dir in args.judgment_dirs:
                _, judgment, _ = load_judgment_bundle(bundle_dir)
                if judgment.get("problemId") != args.problem:
                    raise MathFlowError("knowledge trigger judgment belongs to another problem")
                judgment_id = str(judgment["judgmentId"])
                judgment_ids.append(judgment_id)
                reconciliation = judgment.get("reconciliation")
                if isinstance(reconciliation, dict):
                    reconciliation_dependencies[judgment_id] = {
                        "conflictId": reconciliation["conflictId"],
                        "inputJudgmentIds": list(
                            reconciliation["inputJudgmentIds"]
                        ),
                    }
            conflict_ids = []
            conflict_dependencies: dict[str, list[str]] = {}
            if args.conflicts:
                value = json.loads(args.conflicts.read_text(encoding="utf-8"))
                records = value.get("conflicts") if isinstance(value, dict) else None
                if not isinstance(records, list):
                    raise MathFlowError("conflict input must contain a conflicts array")
                for record in records:
                    if not isinstance(record, dict) or record.get("problemId") != args.problem:
                        raise MathFlowError("knowledge trigger conflict belongs to another problem")
                    conflict_id = str(record.get("conflictId"))
                    conflict_judgments = record.get("judgments")
                    if not isinstance(conflict_judgments, list) or any(
                        not isinstance(item, dict)
                        or not isinstance(item.get("judgmentId"), str)
                        for item in conflict_judgments
                    ):
                        raise MathFlowError(
                            "knowledge trigger conflict has invalid judgment dependencies"
                        )
                    if conflict_id in conflict_dependencies:
                        raise MathFlowError(
                            "knowledge trigger conflict input contains duplicates"
                        )
                    conflict_ids.append(conflict_id)
                    conflict_dependencies[conflict_id] = sorted(
                        {str(item["judgmentId"]) for item in conflict_judgments}
                    )
            result = record_completed_inputs(
                args.scheduler_file,
                args.problem,
                builder_digest,
                judgment_ids,
                conflict_ids,
                args.minimum_interval,
                args.now if args.now is not None else int(time.time()),
                args.projection_digest,
                conflict_dependencies,
                reconciliation_dependencies,
                str(ledger(root, args.problem, args.head)["problemLedgerDigest"]),
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
                args.problem_ledger_digest,
            )
        elif args.command == "publish-batch":
            result = publish_batch(args.projection_dir, args.bundles)
        elif args.command == "github-publish-projection":
            result = publish_github_projection(
                args.projection_dir,
                args.repository,
                args.branch,
                args.message,
                os.environ.get("GITHUB_TOKEN", ""),
            )
        elif args.command == "merge-schedulers":
            states = []
            for path in (args.base, args.ours, args.theirs):
                try:
                    states.append(json.loads(path.read_text(encoding="utf-8")))
                except json.JSONDecodeError as exc:
                    raise MathFlowError(
                        f"scheduler merge input is not valid JSON: {path}"
                    ) from exc
            result = merge_scheduler_states(*states)
            _write_json(result, str(args.output))
            return 0
        elif args.command == "due-projection-plan":
            try:
                scheduler = json.loads(
                    args.scheduler_file.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as exc:
                raise MathFlowError(
                    "due projection scheduler is not valid JSON"
                ) from exc
            result = plan_due_projection_dispatches(
                root,
                scheduler,
                args.now if args.now is not None else int(time.time()),
                args.head,
                args.projection_dir,
            )
            _write_json(result, str(args.output) if args.output else None)
            return 0
        elif args.command == "filter-projection-plan":
            try:
                plan = json.loads(args.plan.read_text(encoding="utf-8"))
                run_history = json.loads(
                    args.run_history.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as exc:
                raise MathFlowError(
                    "projection plan or workflow history is not valid JSON"
                ) from exc
            result = filter_projection_dispatch_history(plan, run_history)
            _write_json(result, str(args.output))
            return 0
        elif args.command == "export-viewer":
            result = export_viewer_data(
                root,
                args.problem,
                args.head,
                args.run_dirs,
                judgment_dirs=args.judgment_dirs,
            )
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
        elif args.command == "context":
            result = materialize_agent_context(
                root,
                args.projection_dir,
                args.problem,
                args.output_dir,
                projection_id=args.projection,
                credit_projection_id=args.credit_projection,
                head=args.head,
                node_ids=args.nodes,
            )
        else:  # pragma: no cover
            raise AssertionError(args.command)
        _write_json(result, None)
        return 0
    except (MathFlowError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
