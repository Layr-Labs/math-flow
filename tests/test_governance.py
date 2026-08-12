from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.coordination import claim_due_build, record_completed_inputs
from math_flow.cli import main
from math_flow.errors import MathFlowError
from math_flow.formation import validate_build_claim
from math_flow.governance import (
    head_bound_comment_approvers,
    list_active_projections,
    resolve_projection,
    validate_admission_pr,
    validate_projection_registry,
)


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2) + "\n")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def projection_spec(projection_id: str = "research-v1") -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "id": projection_id,
        "description": "Test projection",
        "status": "active",
        "engine": "openrouter-repository-v1",
        "allowedProblems": ["*"],
        "primaryJudge": "protocol/judges/primary.json",
        "reconciliationJudge": "protocol/judges/reconciliation.json",
        "knowledgeBuilder": "protocol/judges/builder.json",
        "scheduling": {
            "judgmentMaxParallel": 8,
            "knowledgeMinimumIntervalSeconds": 60,
            "maximumJudgmentsPerBuild": 100,
        },
    }


def overlay_projection_spec(
    projection_id: str = "credit-v1",
) -> dict[str, object]:
    return {
        "schemaVersion": 2,
        "id": projection_id,
        "description": "Test credit overlay",
        "status": "active",
        "engine": "overlay-repository-v1",
        "allowedProblems": ["demo"],
        "runner": {
            "implementation": "openrouter-credit-assignment-v1",
            "spec": "protocol/judges/credit.json",
        },
        "dependencies": [
            {
                "name": "knowledge",
                "projectionId": "research-v1",
                "artifactRole": "knowledge-state",
            }
        ],
        "scheduling": {"minimumIntervalSeconds": 60},
    }


class GovernanceRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Governance Test")
        git(self.root, "config", "user.email", "governance@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        write_json(
            self.root / ".github/math-flow-governance.json",
            {
                "schemaVersion": 1,
                "minimumApprovals": 1,
                "administrators": ["Trusted-Admin"],
            },
        )
        implementations = {
            "primary": "openrouter-markdown-judgment-v1",
            "reconciliation": "openrouter-markdown-reconciliation-v1",
            "builder": "openrouter-knowledge-builder-v1",
        }
        for name, implementation in implementations.items():
            write_json(
                self.root / f"protocol/judges/{name}.json",
                {"implementation": implementation},
            )
        write_json(
            self.root / "protocol/judges/credit.json",
            {"implementation": "openrouter-credit-assignment-v1"},
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Initialize governed repository")
        self.base = git(self.root, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit(self, message: str) -> str:
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", message)
        return git(self.root, "rev-parse", "HEAD")

    def test_problem_admission_requires_configured_admin(self) -> None:
        write(self.root / "problems/new-problem/problem.md", "# New problem\n")
        head = self.commit("Propose a problem")
        with self.assertRaisesRegex(MathFlowError, "needs 1 current-head admin"):
            validate_admission_pr(self.root, self.base, head, ["someone-else"])
        result = validate_admission_pr(
            self.root, self.base, head, ["trusted-admin", "someone-else"]
        )
        self.assertEqual(result["admissionType"], "problem")
        self.assertEqual(result["subjectId"], "new-problem")
        self.assertEqual(result["approvedBy"], ["Trusted-Admin"])

    def test_exact_full_head_comment_authorizes_configured_admin(self) -> None:
        write(self.root / "problems/new-problem/problem.md", "# New problem\n")
        head = self.commit("Propose a problem")
        comments = [
            {
                "author": "Trusted-Admin",
                "body": f"/approve-admission {head}",
            }
        ]
        result = validate_admission_pr(
            self.root,
            self.base,
            head,
            approval_comments=comments,
        )
        self.assertEqual(result["approvedBy"], ["Trusted-Admin"])

        comments_path = self.root / "comments.json"
        write_json(comments_path, comments)
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "validate-admission-pr",
                    "--base",
                    self.base,
                    "--head",
                    head,
                    "--approval-comments",
                    str(comments_path),
                ]
            ),
            0,
        )

    def test_approval_comment_is_exact_head_bound_and_permissioned(self) -> None:
        head = "a" * 40
        comments = [
            {"author": "Trusted-Admin", "body": f"/approve-admission {'b' * 40}"},
            {"author": "Trusted-Admin", "body": f"please /approve-admission {head}"},
            {"author": "Trusted-Admin", "body": f"/approve-admission {head[:12]}"},
            {"author": "Someone-Else", "body": f"/approve-admission {head.upper()}"},
            {"author": "Trusted-Admin", "body": f"\n/approve-admission {head.upper()}\n"},
            {"author": "Trusted-Admin", "body": f"/approve-admission {head}"},
        ]
        self.assertEqual(
            head_bound_comment_approvers(head, comments),
            ["Someone-Else", "Trusted-Admin"],
        )
        with self.assertRaisesRegex(MathFlowError, "full Git SHA"):
            head_bound_comment_approvers("a" * 12, comments)
        with self.assertRaisesRegex(MathFlowError, "JSON array"):
            head_bound_comment_approvers(head, {})
        with self.assertRaisesRegex(MathFlowError, "invalid shape"):
            head_bound_comment_approvers(head, [{"author": "Trusted-Admin"}])

        write(self.root / "problems/new-problem/problem.md", "# New problem\n")
        actual_head = self.commit("Propose a problem")
        with self.assertRaisesRegex(MathFlowError, "needs 1 current-head admin"):
            validate_admission_pr(
                self.root,
                self.base,
                actual_head,
                approval_comments=[
                    {
                        "author": "Someone-Else",
                        "body": f"/approve-admission {actual_head}",
                    }
                ],
            )

    def test_problem_admission_must_be_a_separate_one_file_pr(self) -> None:
        write(self.root / "problems/new-problem/problem.md", "# New problem\n")
        write(self.root / "docs/extra.md", "mixed maintenance\n")
        head = self.commit("Mix admission and maintenance")
        with self.assertRaisesRegex(MathFlowError, "separate one-file PRs"):
            validate_admission_pr(self.root, self.base, head, ["Trusted-Admin"])

    def test_governed_definition_cannot_be_renamed_out_of_policy_scope(self) -> None:
        git(
            self.root,
            "mv",
            "problems/demo/problem.md",
            "problems/demo/renamed.md",
        )
        head = self.commit("Rename governed statement")
        with self.assertRaisesRegex(MathFlowError, "not deleted or renamed"):
            validate_admission_pr(self.root, self.base, head, ["Trusted-Admin"])

    def test_projection_registry_resolves_approved_paths_and_policy(self) -> None:
        write_json(
            self.root / "protocol/projections/research-v1.json",
            projection_spec(),
        )
        head = self.commit("Propose projection")
        admission = validate_admission_pr(
            self.root, self.base, head, ["Trusted-Admin"]
        )
        self.assertEqual(admission["admissionType"], "projection")
        self.assertEqual(
            validate_projection_registry(self.root), {"projections": 1, "active": 1}
        )
        resolved = resolve_projection(self.root, "research-v1", "demo", head)
        self.assertEqual(resolved["primaryJudge"], "protocol/judges/primary.json")
        self.assertEqual(resolved["scheduling"]["judgmentMaxParallel"], 8)
        self.assertRegex(resolved["projectionSpecDigest"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(resolved["dependencies"], [])

    def test_projection_dependencies_are_governed_typed_and_resolved(self) -> None:
        producer = projection_spec("producer-v1")
        consumer = projection_spec("credit-v1")
        consumer["dependencies"] = [
            {
                "name": "knowledge",
                "projectionId": "producer-v1",
                "artifactRole": "knowledge-state",
            }
        ]
        write_json(
            self.root / "protocol/projections/producer-v1.json", producer
        )
        write_json(self.root / "protocol/projections/credit-v1.json", consumer)
        head = self.commit("Add typed projection dependency")

        self.assertEqual(
            validate_projection_registry(self.root),
            {"projections": 2, "active": 2},
        )
        resolved = resolve_projection(self.root, "credit-v1", "demo", head)
        self.assertEqual(
            resolved["dependencies"],
            [
                {
                    "name": "knowledge",
                    "projectionId": "producer-v1",
                    "projectionSpecDigest": resolve_projection(
                        self.root, "producer-v1", "demo", head
                    )["projectionSpecDigest"],
                    "artifactRole": "knowledge-state",
                }
            ],
        )

    def test_overlay_projection_uses_allowlisted_runner_and_engine_filter(self) -> None:
        write_json(
            self.root / "protocol/projections/research-v1.json",
            projection_spec(),
        )
        write_json(
            self.root / "protocol/projections/credit-v1.json",
            overlay_projection_spec(),
        )
        head = self.commit("Add credit overlay")
        resolved = resolve_projection(self.root, "credit-v1", "demo", head)
        self.assertEqual(resolved["engine"], "overlay-repository-v1")
        self.assertEqual(
            resolved["runner"]["implementation"],
            "openrouter-credit-assignment-v1",
        )
        self.assertNotIn("knowledgeBuilder", resolved)
        knowledge_only = list_active_projections(
            self.root,
            "demo",
            head,
            engine="openrouter-repository-v1",
        )
        self.assertEqual(
            [item["projectionId"] for item in knowledge_only["projections"]],
            ["research-v1"],
        )
        overlays = list_active_projections(
            self.root,
            "demo",
            head,
            engine="overlay-repository-v1",
        )
        self.assertEqual(
            [item["projectionId"] for item in overlays["projections"]],
            ["credit-v1"],
        )

        invalid = overlay_projection_spec()
        invalid["runner"]["implementation"] = "repository-python-path-v1"
        write_json(
            self.root / "protocol/projections/credit-v1.json", invalid
        )
        with self.assertRaisesRegex(MathFlowError, "unsupported runner"):
            validate_projection_registry(self.root)

    def test_overlay_calendar_cadence_is_governed_and_fail_closed(self) -> None:
        write_json(
            self.root / "protocol/projections/research-v1.json",
            projection_spec(),
        )
        calendar = overlay_projection_spec()
        calendar["scheduling"]["utcCalendarPeriod"] = {"unit": "day"}
        write_json(
            self.root / "protocol/projections/credit-v1.json", calendar
        )
        head = self.commit("Add daily credit cadence")
        resolved = resolve_projection(self.root, "credit-v1", "demo", head)
        self.assertEqual(
            resolved["scheduling"],
            {
                "minimumIntervalSeconds": 60,
                "utcCalendarPeriod": {"unit": "day"},
            },
        )

        for invalid_period in (
            {"unit": "week"},
            {"unit": "day", "timeZone": "America/Los_Angeles"},
            "day",
        ):
            invalid = overlay_projection_spec()
            invalid["scheduling"]["utcCalendarPeriod"] = invalid_period
            write_json(
                self.root / "protocol/projections/credit-v1.json", invalid
            )
            with self.assertRaisesRegex(MathFlowError, "utcCalendarPeriod"):
                validate_projection_registry(self.root)

        invalid_interval = overlay_projection_spec()
        invalid_interval["scheduling"] = {
            "minimumIntervalSeconds": 3_601,
            "utcCalendarPeriod": {"unit": "hour"},
        }
        write_json(
            self.root / "protocol/projections/credit-v1.json",
            invalid_interval,
        )
        with self.assertRaisesRegex(MathFlowError, "cannot exceed"):
            validate_projection_registry(self.root)

    def test_projection_dependency_graph_rejects_unknown_cycles_and_gaps(self) -> None:
        consumer = projection_spec("consumer-v1")
        consumer["dependencies"] = [
            {
                "name": "knowledge",
                "projectionId": "missing-v1",
                "artifactRole": "knowledge-state",
            }
        ]
        write_json(
            self.root / "protocol/projections/consumer-v1.json", consumer
        )
        with self.assertRaisesRegex(MathFlowError, "unknown projection"):
            validate_projection_registry(self.root)

        producer = projection_spec("producer-v1")
        producer["dependencies"] = [
            {
                "name": "consumer",
                "projectionId": "consumer-v1",
                "artifactRole": "knowledge-state",
            }
        ]
        consumer["dependencies"][0]["projectionId"] = "producer-v1"
        write_json(
            self.root / "protocol/projections/consumer-v1.json", consumer
        )
        write_json(
            self.root / "protocol/projections/producer-v1.json", producer
        )
        with self.assertRaisesRegex(MathFlowError, "contains a cycle"):
            validate_projection_registry(self.root)

        producer.pop("dependencies")
        producer["allowedProblems"] = ["some-other-problem"]
        write_json(
            self.root / "protocol/projections/producer-v1.json", producer
        )
        with self.assertRaisesRegex(MathFlowError, "does not cover every"):
            validate_projection_registry(self.root)

    def test_lists_only_active_projections_allowed_for_problem_deterministically(self) -> None:
        wildcard = projection_spec("wildcard-v1")
        restricted = projection_spec("restricted-v1")
        restricted["allowedProblems"] = ["demo"]
        disabled = projection_spec("disabled-v1")
        disabled["status"] = "disabled"
        elsewhere = projection_spec("elsewhere-v1")
        elsewhere["allowedProblems"] = ["another-problem"]
        for spec in [wildcard, restricted, disabled, elsewhere]:
            write_json(
                self.root / f"protocol/projections/{spec['id']}.json",
                spec,
            )
        head = self.commit("Add projection matrix")

        first = list_active_projections(self.root, "demo", head)
        second = list_active_projections(self.root, "demo", head)
        self.assertEqual(first, second)
        self.assertEqual(
            [item["projectionId"] for item in first["projections"]],
            ["restricted-v1", "wildcard-v1"],
        )

        output = self.root / "active-projections.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "list-active-projections",
                    "--problem",
                    "demo",
                    "--head",
                    head,
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), first)

    def test_projection_cannot_reference_an_arbitrary_path(self) -> None:
        invalid = projection_spec()
        invalid["primaryJudge"] = ".github/workflows/anything.yml"
        write_json(self.root / "protocol/projections/research-v1.json", invalid)
        with self.assertRaisesRegex(MathFlowError, "protocol/judges"):
            validate_projection_registry(self.root)

    def test_ordinary_contribution_does_not_require_governance_approval(self) -> None:
        write(
            self.root / "problems/demo/contributions/proof/README.md",
            "# Proof\n",
        )
        head = self.commit("Add contribution")
        result = validate_admission_pr(self.root, self.base, head)
        self.assertEqual(result["admissionType"], "not-applicable")
        self.assertFalse(result["approvalRequired"])


class ProjectionLaneTests(unittest.TestCase):
    def test_projection_digest_isolates_same_builder_into_distinct_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scheduler = root / "scheduler.json"
            builder = "sha256:" + "1" * 64
            judgment = "sha256:" + "2" * 64
            first_projection = "sha256:" + "3" * 64
            second_projection = "sha256:" + "4" * 64
            first = record_completed_inputs(
                scheduler,
                "demo",
                builder,
                [judgment],
                [],
                0,
                10,
                first_projection,
            )
            second = record_completed_inputs(
                scheduler,
                "demo",
                builder,
                [judgment],
                [],
                0,
                10,
                second_projection,
            )
            self.assertNotEqual(first["laneId"], second["laneId"])
            claim = claim_due_build(scheduler, first["laneId"], 10, 10)
            self.assertIsNotNone(claim)
            self.assertEqual(claim["projectionSpecDigest"], first_projection)
            validated = validate_build_claim(claim, "demo", builder)
            self.assertEqual(validated["projectionSpecDigest"], first_projection)


class CurrentRegistryTests(unittest.TestCase):
    def test_repository_projection_registry_is_valid(self) -> None:
        root = Path(__file__).parents[1]
        result = validate_projection_registry(root)
        self.assertGreaterEqual(result["projections"], 1)
        resolved = resolve_projection(
            root, "openrouter-research-v1", "triangle-midpoints", "WORKTREE"
        )
        self.assertEqual(resolved["problemId"], "triangle-midpoints")

    def test_credit_workflow_rechecks_canonical_and_projection_state(self) -> None:
        root = Path(__file__).parents[1]
        workflow = (
            root / ".github/workflows/project-credit.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "git fetch origin +refs/heads/main:refs/remotes/origin/main",
            workflow,
        )
        self.assertIn("--head refs/remotes/origin/main", workflow)
        self.assertIn("--canonical-ref refs/remotes/origin/main", workflow)
        self.assertIn("dependencyStateDigest", workflow)
        self.assertIn("problemLedgerDigest", workflow)
        self.assertIn("runnerSpecDigest", workflow)

    def test_direction_events_refresh_only_the_repository_catalog(self) -> None:
        root = Path(__file__).parents[1]
        auto_merge = (
            root / ".github/workflows/auto-merge-contribution.yml"
        ).read_text(encoding="utf-8")
        refresh = (
            root / ".github/workflows/refresh-viewer-catalog.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("transaction_kind == 'direction-event'", auto_merge)
        self.assertIn("gh workflow run refresh-viewer-catalog.yml", auto_merge)
        self.assertIn("export-viewer-catalog", refresh)
        self.assertIn("--canonical-ref refs/remotes/origin/main", refresh)
        self.assertIn("github-publish-projection", refresh)
        self.assertNotIn("OPENROUTER_API_KEY", refresh)


if __name__ == "__main__":
    unittest.main()
