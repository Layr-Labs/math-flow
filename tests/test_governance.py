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


if __name__ == "__main__":
    unittest.main()
