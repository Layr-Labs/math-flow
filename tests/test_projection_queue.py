from __future__ import annotations

import copy
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.coordination import (
    claim_due_build,
    fail_build,
    load_scheduler,
    record_completed_inputs,
)
from math_flow.cli import main
from math_flow.errors import MathFlowError
from math_flow.governance import resolve_projection
from math_flow.projection_queue import (
    filter_projection_dispatch_history,
    merge_scheduler_states,
    plan_due_projection_dispatches,
    validate_scheduler_state,
)
from math_flow.repository import ledger, sha256_json


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


def projection_spec(projection_id: str) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "id": projection_id,
        "description": f"Projection {projection_id}",
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


class ProjectionQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Projection Queue Test")
        git(self.root, "config", "user.email", "queue@example.com")
        for problem in ("first-problem", "second-problem"):
            write(self.root / f"problems/{problem}/problem.md", f"# {problem}\n")
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
        for projection in ("alpha-v1", "zeta-v1"):
            write_json(
                self.root / f"protocol/projections/{projection}.json",
                projection_spec(projection),
            )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Initialize queue test repository")
        self.head = git(self.root, "rev-parse", "HEAD")
        builder_spec = {"implementation": implementations["builder"]}
        self.builder_digest = f"sha256:{sha256_json(builder_spec)}"
        self.judgment_number = 0

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def projection_digest(self, projection: str, problem: str) -> str:
        resolved = resolve_projection(self.root, projection, problem, self.head)
        return str(resolved["projectionSpecDigest"])

    def record(
        self,
        scheduler: Path,
        problem: str,
        projection: str,
        *,
        now: int = 10,
        count: int = 1,
    ) -> dict[str, object]:
        judgments = []
        for _ in range(count):
            self.judgment_number += 1
            judgments.append(f"sha256:{self.judgment_number:064x}")
        return record_completed_inputs(
            scheduler,
            problem,
            self.builder_digest,
            judgments,
            [],
            minimum_interval_seconds=60,
            now=now,
            projection_spec_digest=self.projection_digest(projection, problem),
        )

    def state_with_lane(
        self, name: str, problem: str, projection: str
    ) -> dict[str, object]:
        scheduler = self.root / f"{name}-scheduler.json"
        self.record(scheduler, problem, projection, count=0)
        return load_scheduler(scheduler)

    def add_contribution(self, problem: str, contribution: str = "first") -> str:
        write(
            self.root
            / f"problems/{problem}/contributions/{contribution}/submission.md",
            f"# {contribution}\n",
        )
        git(self.root, "add", f"problems/{problem}/contributions/{contribution}")
        git(self.root, "commit", "-qm", f"Add {contribution} to {problem}")
        self.head = git(self.root, "rev-parse", "HEAD")
        return self.head

    def publish_latest_state(
        self,
        scheduler: Path,
        projection_root: Path,
        problem: str,
        projection: str,
        *,
        ledger_head: str | None = None,
    ) -> dict[str, object]:
        self.record(scheduler, problem, projection, count=0)
        state = load_scheduler(scheduler)
        projection_digest = self.projection_digest(projection, problem)
        identifier = next(
            lane_id
            for lane_id, lane in state["lanes"].items()
            if lane.get("projectionSpecDigest") == projection_digest
            and lane.get("problemId") == problem
        )
        source = ledger(self.root, problem, ledger_head or self.head)
        manifest = {
            "protocolVersion": 1,
            "runKind": "knowledge-build",
            "problemId": problem,
            "ledgerHead": source["ledgerHead"],
            "problemLedgerHead": source["problemLedgerHead"],
            "problemLedgerDigest": source["problemLedgerDigest"],
            "judgeSpec": {"id": "builder", "digest": self.builder_digest},
            "inputs": {
                "laneId": identifier,
                "problemId": problem,
                "builderSpecDigest": self.builder_digest,
                "projectionSpecDigest": projection_digest,
            },
            "artifacts": [],
        }
        rendered = json.dumps(manifest, indent=2) + "\n"
        run_digest = sha256_bytes(rendered.encode("utf-8"))
        digest_hex = run_digest.removeprefix("sha256:")
        write(
            projection_root
            / f"objects/knowledge-build/{digest_hex[:2]}/{digest_hex}/run.json",
            rendered,
        )
        lane = state["lanes"][identifier]
        lane["latestStateRun"] = run_digest
        lane["lastCompletedAt"] = 10
        lane["nextEligibleAt"] = None
        write_json(scheduler, state)
        return lane

    def test_three_way_merge_accepts_disjoint_and_identical_lane_changes(self) -> None:
        empty = {"schemaVersion": 1, "lanes": {}}
        ours = self.state_with_lane("ours", "first-problem", "zeta-v1")
        theirs = self.state_with_lane("theirs", "second-problem", "alpha-v1")
        merged = merge_scheduler_states(empty, ours, theirs)
        self.assertEqual(
            list(merged["lanes"]), sorted([*ours["lanes"], *theirs["lanes"]])
        )
        for identifier, lane in {**ours["lanes"], **theirs["lanes"]}.items():
            self.assertEqual(merged["lanes"][identifier], lane)

        identical = merge_scheduler_states(empty, ours, copy.deepcopy(ours))
        self.assertEqual(identical, ours)
        self.assertIsNot(identical, ours)

    def test_three_way_merge_rejects_divergent_same_lane_changes(self) -> None:
        base = self.state_with_lane("base", "first-problem", "alpha-v1")
        ours = copy.deepcopy(base)
        theirs = copy.deepcopy(base)
        identifier = next(iter(base["lanes"]))
        ours["lanes"][identifier]["minimumIntervalSeconds"] = 30
        theirs["lanes"][identifier]["minimumIntervalSeconds"] = 90
        with self.assertRaisesRegex(MathFlowError, "changed divergently"):
            merge_scheduler_states(base, ours, theirs)

    def test_merge_schedulers_cli_round_trips_output_and_reports_conflicts(self) -> None:
        empty = {"schemaVersion": 1, "lanes": {}}
        ours = self.state_with_lane("cli-ours", "first-problem", "zeta-v1")
        theirs = self.state_with_lane("cli-theirs", "second-problem", "alpha-v1")
        paths = {
            "base": self.root / "cli-base.json",
            "ours": self.root / "cli-ours.json",
            "theirs": self.root / "cli-theirs.json",
        }
        for name, state in (("base", empty), ("ours", ours), ("theirs", theirs)):
            write_json(paths[name], state)
        output = self.root / "results/merged-scheduler.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "merge-schedulers",
                    "--base",
                    str(paths["base"]),
                    "--ours",
                    str(paths["ours"]),
                    "--theirs",
                    str(paths["theirs"]),
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        self.assertEqual(
            json.loads(output.read_text(encoding="utf-8")),
            merge_scheduler_states(empty, ours, theirs),
        )

        identifier = next(iter(ours["lanes"]))
        base = copy.deepcopy(ours)
        our_conflict = copy.deepcopy(base)
        their_conflict = copy.deepcopy(base)
        our_conflict["lanes"][identifier]["minimumIntervalSeconds"] = 30
        their_conflict["lanes"][identifier]["minimumIntervalSeconds"] = 90
        for name, state in (
            ("base", base),
            ("ours", our_conflict),
            ("theirs", their_conflict),
        ):
            write_json(paths[name], state)
        conflict_output = self.root / "results/conflicted-scheduler.json"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = main(
                [
                    "--root",
                    str(self.root),
                    "merge-schedulers",
                    "--base",
                    str(paths["base"]),
                    "--ours",
                    str(paths["ours"]),
                    "--theirs",
                    str(paths["theirs"]),
                    "--output",
                    str(conflict_output),
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("changed divergently", stderr.getvalue())
        self.assertFalse(conflict_output.exists())

    def test_three_way_merge_handles_an_unopposed_lane_deletion(self) -> None:
        base = self.state_with_lane("base-delete", "first-problem", "alpha-v1")
        empty = {"schemaVersion": 1, "lanes": {}}
        self.assertEqual(
            merge_scheduler_states(base, empty, copy.deepcopy(base)), empty
        )

    def test_scheduler_validation_rejects_malformed_lane_and_active_lease(self) -> None:
        scheduler = self.root / "malformed-scheduler.json"
        lane = self.record(
            scheduler, "first-problem", "alpha-v1", now=10, count=2
        )
        claim = claim_due_build(scheduler, str(lane["laneId"]), 10, 1)
        self.assertIsNotNone(claim)
        state = load_scheduler(scheduler)
        malformed = copy.deepcopy(state)
        identifier = next(iter(malformed["lanes"]))
        malformed["lanes"][identifier]["activeBuild"]["buildToken"] = (
            "sha256:" + "f" * 64
        )
        with self.assertRaisesRegex(MathFlowError, "invalid buildToken"):
            validate_scheduler_state(malformed)

        mismatched = copy.deepcopy(state)
        mismatched["lanes"][identifier]["problemId"] = "second-problem"
        with self.assertRaisesRegex(MathFlowError, "identity fields"):
            validate_scheduler_state(mismatched)

    def test_scheduler_validation_accepts_and_checks_dependency_maps(self) -> None:
        scheduler = self.root / "dependency-scheduler.json"
        primary_one = "sha256:" + "1" * 64
        primary_two = "sha256:" + "2" * 64
        conflict = "sha256:" + "3" * 64
        reconciliation = "sha256:" + "4" * 64
        record_completed_inputs(
            scheduler,
            "first-problem",
            self.builder_digest,
            [primary_one, primary_two, reconciliation],
            [conflict],
            minimum_interval_seconds=60,
            now=10,
            projection_spec_digest=self.projection_digest(
                "alpha-v1", "first-problem"
            ),
            conflict_dependencies={conflict: [primary_one, primary_two]},
            reconciliation_dependencies={
                reconciliation: {
                    "conflictId": conflict,
                    "inputJudgmentIds": [primary_one, primary_two],
                }
            },
        )
        state = load_scheduler(scheduler)
        self.assertEqual(validate_scheduler_state(state), state)

        unpaired = copy.deepcopy(state)
        identifier = next(iter(unpaired["lanes"]))
        del unpaired["lanes"][identifier]["reconciliationDependencies"]
        with self.assertRaisesRegex(MathFlowError, "pair dependency maps"):
            validate_scheduler_state(unpaired)

        inconsistent = copy.deepcopy(state)
        inconsistent["lanes"][identifier]["reconciliationDependencies"][
            reconciliation
        ]["inputJudgmentIds"] = [primary_one, reconciliation]
        with self.assertRaisesRegex(MathFlowError, "do not match its conflict"):
            validate_scheduler_state(inconsistent)

    def test_planner_groups_due_projections_by_problem_deterministically(self) -> None:
        scheduler = self.root / "due-scheduler.json"
        self.record(scheduler, "first-problem", "zeta-v1")
        self.record(scheduler, "second-problem", "alpha-v1")
        self.record(scheduler, "first-problem", "alpha-v1")
        state = load_scheduler(scheduler)

        expected_alpha_first = resolve_projection(
            self.root, "alpha-v1", "first-problem", self.head
        )
        expected_zeta_first = resolve_projection(
            self.root, "zeta-v1", "first-problem", self.head
        )
        expected_alpha_second = resolve_projection(
            self.root, "alpha-v1", "second-problem", self.head
        )
        expected = {
            "schemaVersion": 1,
            "repositoryHead": self.head,
            "problems": [
                {
                    "problemId": "first-problem",
                    "projections": [expected_alpha_first, expected_zeta_first],
                },
                {
                    "problemId": "second-problem",
                    "projections": [expected_alpha_second],
                },
            ],
        }
        first = plan_due_projection_dispatches(
            self.root, state, now=10, repository_head=self.head
        )
        second = plan_due_projection_dispatches(
            self.root, copy.deepcopy(state), now=10, repository_head=self.head
        )
        self.assertEqual(first, expected)
        self.assertEqual(second, expected)

    def test_due_projection_plan_cli_round_trips_resolved_queues(self) -> None:
        scheduler = self.root / "cli-due-scheduler.json"
        self.record(scheduler, "first-problem", "zeta-v1")
        self.record(scheduler, "first-problem", "alpha-v1")
        state = load_scheduler(scheduler)
        expected = plan_due_projection_dispatches(
            self.root, state, now=10, repository_head=self.head
        )
        output = self.root / "results/due-projections.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "due-projection-plan",
                    "--scheduler-file",
                    str(scheduler),
                    "--head",
                    self.head,
                    "--now",
                    "10",
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        actual = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)
        self.assertEqual(
            [
                item["projectionId"]
                for item in actual["problems"][0]["projections"]
            ],
            ["alpha-v1", "zeta-v1"],
        )

    def test_history_filter_caps_one_projection_without_blocking_another(self) -> None:
        plan = {
            "schemaVersion": 1,
            "repositoryHead": self.head,
            "problems": [
                {
                    "problemId": "first-problem",
                    "projections": [
                        resolve_projection(
                            self.root, "alpha-v1", "first-problem", self.head
                        ),
                        resolve_projection(
                            self.root, "zeta-v1", "first-problem", self.head
                        ),
                    ],
                }
            ],
        }

        def run(
            run_id: int,
            projection: str,
            *,
            status: str = "completed",
            conclusion: str | None = "failure",
            head: str | None = None,
        ) -> dict[str, object]:
            return {
                "conclusion": conclusion,
                "databaseId": run_id,
                "displayTitle": f"Project {projection}/first-problem",
                "headSha": head or self.head,
                "status": status,
            }

        history = [
            run(1, "alpha-v1", status="in_progress", conclusion=None),
            run(2, "zeta-v1"),
            run(3, "zeta-v1"),
        ]
        filtered = filter_projection_dispatch_history(plan, history)
        self.assertEqual(
            [
                item["projectionId"]
                for item in filtered["problems"][0]["projections"]
            ],
            ["zeta-v1"],
        )

        capped = filter_projection_dispatch_history(
            plan,
            [*history, run(4, "zeta-v1"), run(5, "zeta-v1"), run(6, "zeta-v1")],
        )
        self.assertEqual(capped["problems"], [])

        reset = filter_projection_dispatch_history(
            plan,
            [
                *history,
                run(4, "zeta-v1"),
                run(5, "zeta-v1"),
                run(6, "zeta-v1"),
                run(7, "zeta-v1", conclusion="success"),
            ],
        )
        self.assertEqual(
            [item["projectionId"] for item in reset["problems"][0]["projections"]],
            ["zeta-v1"],
        )

        plan_path = self.root / "results/history-plan.json"
        history_path = self.root / "results/history-runs.json"
        output = self.root / "results/filtered-history-plan.json"
        write_json(plan_path, plan)
        write_json(history_path, history)
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "filter-projection-plan",
                    "--plan",
                    str(plan_path),
                    "--run-history",
                    str(history_path),
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), filtered)

    def test_recovery_planner_queues_never_run_active_projections(self) -> None:
        self.add_contribution("first-problem")
        projection_root = self.root / "published"
        output = self.root / "results/recovered-projections.json"
        scheduler = self.root / "empty-scheduler.json"
        write_json(scheduler, {"schemaVersion": 1, "lanes": {}})

        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "due-projection-plan",
                    "--scheduler-file",
                    str(scheduler),
                    "--projection-dir",
                    str(projection_root),
                    "--head",
                    self.head,
                    "--now",
                    "10",
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        plan = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(
            [
                (problem["problemId"], [item["projectionId"] for item in problem["projections"]])
                for problem in plan["problems"]
            ],
            [("first-problem", ["alpha-v1", "zeta-v1"])],
        )

    def test_recovery_planner_queues_idle_lane_with_stale_state(self) -> None:
        self.add_contribution("first-problem", "initial")
        old_head = self.head
        scheduler = self.root / "stale-scheduler.json"
        projection_root = self.root / "published-stale"
        self.publish_latest_state(
            scheduler,
            projection_root,
            "first-problem",
            "alpha-v1",
            ledger_head=old_head,
        )
        self.add_contribution("first-problem", "later")
        self.publish_latest_state(
            scheduler, projection_root, "first-problem", "zeta-v1"
        )

        plan = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=10,
            repository_head=self.head,
            projection_root=projection_root,
        )
        self.assertEqual(len(plan["problems"]), 1)
        self.assertEqual(
            [item["projectionId"] for item in plan["problems"][0]["projections"]],
            ["alpha-v1"],
        )

    def test_recovery_planner_ignores_disabled_and_unknown_stale_lanes(self) -> None:
        self.add_contribution("first-problem")
        scheduler = self.root / "disabled-scheduler.json"
        self.record(scheduler, "first-problem", "zeta-v1")
        record_completed_inputs(
            scheduler,
            "first-problem",
            self.builder_digest,
            ["sha256:" + "e" * 64],
            [],
            minimum_interval_seconds=0,
            now=10,
            projection_spec_digest="sha256:" + "f" * 64,
        )
        disabled = projection_spec("zeta-v1")
        disabled["status"] = "disabled"
        write_json(self.root / "protocol/projections/zeta-v1.json", disabled)
        git(self.root, "add", "protocol/projections/zeta-v1.json")
        git(self.root, "commit", "-qm", "Disable zeta projection")
        self.head = git(self.root, "rev-parse", "HEAD")

        plan = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=10,
            repository_head=self.head,
            projection_root=self.root / "published-disabled",
        )
        self.assertEqual(
            [item["projectionId"] for item in plan["problems"][0]["projections"]],
            ["alpha-v1"],
        )

    def test_recovery_planner_excludes_current_and_empty_problem_projections(self) -> None:
        self.add_contribution("first-problem")
        scheduler = self.root / "current-scheduler.json"
        projection_root = self.root / "published-current"
        for projection in ("alpha-v1", "zeta-v1"):
            self.publish_latest_state(
                scheduler, projection_root, "first-problem", projection
            )

        plan = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=10,
            repository_head=self.head,
            projection_root=projection_root,
        )
        self.assertEqual(plan["problems"], [])

    def test_recovery_planner_queues_missing_latest_bundle(self) -> None:
        self.add_contribution("first-problem")
        scheduler = self.root / "missing-latest-scheduler.json"
        projection_root = self.root / "published-missing"
        current = self.publish_latest_state(
            scheduler, projection_root, "first-problem", "zeta-v1"
        )
        self.record(scheduler, "first-problem", "alpha-v1", count=0)
        state = load_scheduler(scheduler)
        alpha_digest = self.projection_digest("alpha-v1", "first-problem")
        alpha = next(
            lane
            for lane in state["lanes"].values()
            if lane.get("projectionSpecDigest") == alpha_digest
        )
        alpha["latestStateRun"] = "sha256:" + "9" * 64
        alpha["lastCompletedAt"] = 10
        alpha["nextEligibleAt"] = None
        write_json(scheduler, state)
        self.assertIsNotNone(current["latestStateRun"])

        plan = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=10,
            repository_head=self.head,
            projection_root=projection_root,
        )
        self.assertEqual(
            [item["projectionId"] for item in plan["problems"][0]["projections"]],
            ["alpha-v1"],
        )

    def test_recovery_planner_caps_failures_until_problem_ledger_changes(self) -> None:
        self.add_contribution("first-problem", "initial")
        scheduler = self.root / "failed-scheduler.json"
        projection_root = self.root / "published-failed"
        self.publish_latest_state(
            scheduler, projection_root, "first-problem", "zeta-v1"
        )
        lane = self.record(scheduler, "first-problem", "alpha-v1")
        problem_digest = str(
            ledger(self.root, "first-problem", self.head)["problemLedgerDigest"]
        )
        now = 10
        for expected_count in range(1, 6):
            claim = claim_due_build(
                scheduler, str(lane["laneId"]), now, maximum_judgments=100
            )
            self.assertIsNotNone(claim)
            lane = fail_build(
                scheduler,
                str(lane["laneId"]),
                str(claim["buildToken"]),
                now,
                problem_digest,
            )
            self.assertEqual(
                lane["lastFailure"]["consecutiveFailures"], expected_count
            )
            now = int(lane["nextEligibleAt"])

        capped = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=now,
            repository_head=self.head,
            projection_root=projection_root,
        )
        self.assertEqual(capped["problems"], [])

        self.add_contribution("first-problem", "new-evidence")
        recovered = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=now,
            repository_head=self.head,
            projection_root=projection_root,
        )
        self.assertEqual(
            [
                item["projectionId"]
                for item in recovered["problems"][0]["projections"]
            ],
            ["alpha-v1", "zeta-v1"],
        )

    def test_recovery_planner_validates_latest_bundle_address_and_lane(self) -> None:
        self.add_contribution("first-problem")
        scheduler = self.root / "verified-latest-scheduler.json"
        projection_root = self.root / "published-verified"
        lane = self.publish_latest_state(
            scheduler, projection_root, "first-problem", "alpha-v1"
        )
        self.publish_latest_state(
            scheduler, projection_root, "first-problem", "zeta-v1"
        )
        digest_hex = str(lane["latestStateRun"]).removeprefix("sha256:")
        run_path = (
            projection_root
            / f"objects/knowledge-build/{digest_hex[:2]}/{digest_hex}/run.json"
        )
        original = run_path.read_text(encoding="utf-8")
        manifest = json.loads(original)
        manifest["unexpected"] = True
        write_json(run_path, manifest)
        with self.assertRaisesRegex(MathFlowError, "content address"):
            plan_due_projection_dispatches(
                self.root,
                load_scheduler(scheduler),
                now=10,
                repository_head=self.head,
                projection_root=projection_root,
            )

        write(run_path, original)
        manifest = json.loads(original)
        manifest["inputs"]["projectionSpecDigest"] = "sha256:" + "f" * 64
        rendered = json.dumps(manifest, indent=2) + "\n"
        mismatched_digest = sha256_bytes(rendered.encode("utf-8"))
        mismatched_hex = mismatched_digest.removeprefix("sha256:")
        write(
            projection_root
            / f"objects/knowledge-build/{mismatched_hex[:2]}/{mismatched_hex}/run.json",
            rendered,
        )
        state = load_scheduler(scheduler)
        state["lanes"][str(lane["laneId"])]["latestStateRun"] = mismatched_digest
        write_json(scheduler, state)
        with self.assertRaisesRegex(MathFlowError, "projection lane"):
            plan_due_projection_dispatches(
                self.root,
                load_scheduler(scheduler),
                now=10,
                repository_head=self.head,
                projection_root=projection_root,
            )

    def test_planner_ignores_idle_active_and_future_lanes(self) -> None:
        scheduler = self.root / "filtered-scheduler.json"
        self.record(scheduler, "first-problem", "alpha-v1", now=10)
        self.record(scheduler, "first-problem", "zeta-v1", now=20)
        active = self.record(
            scheduler, "second-problem", "alpha-v1", now=10, count=2
        )
        claim_due_build(scheduler, str(active["laneId"]), 10, 1)
        self.record(
            scheduler, "second-problem", "zeta-v1", now=10, count=0
        )

        plan = plan_due_projection_dispatches(
            self.root,
            load_scheduler(scheduler),
            now=10,
            repository_head=self.head,
        )
        self.assertEqual(len(plan["problems"]), 1)
        self.assertEqual(plan["problems"][0]["problemId"], "first-problem")
        self.assertEqual(
            [item["projectionId"] for item in plan["problems"][0]["projections"]],
            ["alpha-v1"],
        )

    def test_planner_rejects_due_lane_with_unknown_projection(self) -> None:
        scheduler = self.root / "unknown-scheduler.json"
        record_completed_inputs(
            scheduler,
            "first-problem",
            self.builder_digest,
            ["sha256:" + "1" * 64],
            [],
            minimum_interval_seconds=0,
            now=10,
            projection_spec_digest="sha256:" + "f" * 64,
        )
        with self.assertRaisesRegex(MathFlowError, "active governed projections"):
            plan_due_projection_dispatches(
                self.root,
                load_scheduler(scheduler),
                now=10,
                repository_head=self.head,
            )

    def test_planner_rejects_due_lane_with_mismatched_governed_interval(self) -> None:
        scheduler = self.root / "policy-scheduler.json"
        lane = self.record(scheduler, "first-problem", "alpha-v1", now=10)
        state = load_scheduler(scheduler)
        state["lanes"][str(lane["laneId"])]["minimumIntervalSeconds"] = 59
        with self.assertRaisesRegex(MathFlowError, "interval does not match"):
            plan_due_projection_dispatches(
                self.root, state, now=10, repository_head=self.head
            )

    def test_planner_pins_governance_to_the_requested_repository_head(self) -> None:
        scheduler = self.root / "head-scheduler.json"
        self.record(scheduler, "first-problem", "alpha-v1", now=10)
        state = load_scheduler(scheduler)
        old_plan = plan_due_projection_dispatches(
            self.root, state, now=10, repository_head=self.head
        )
        self.assertEqual(
            old_plan["problems"][0]["projections"][0]["projectionId"], "alpha-v1"
        )

        disabled = projection_spec("alpha-v1")
        disabled["status"] = "disabled"
        write_json(self.root / "protocol/projections/alpha-v1.json", disabled)
        git(self.root, "add", "protocol/projections/alpha-v1.json")
        git(self.root, "commit", "-qm", "Disable alpha projection")
        new_head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "active governed projections"):
            plan_due_projection_dispatches(
                self.root, state, now=10, repository_head=new_head
            )

    def test_planner_rejects_invalid_time_and_malformed_pending_lane(self) -> None:
        scheduler = self.root / "invalid-scheduler.json"
        self.record(scheduler, "first-problem", "alpha-v1", now=10)
        state = load_scheduler(scheduler)
        with self.assertRaisesRegex(MathFlowError, "nonnegative integer"):
            plan_due_projection_dispatches(
                self.root, state, now=True, repository_head=self.head
            )

        malformed = copy.deepcopy(state)
        identifier = next(iter(malformed["lanes"]))
        malformed["lanes"][identifier]["pendingJudgmentIds"] = ["not-a-digest"]
        with self.assertRaisesRegex(MathFlowError, "SHA-256 digest"):
            plan_due_projection_dispatches(
                self.root, malformed, now=10, repository_head=self.head
            )

        explicit_null_projection = copy.deepcopy(state)
        explicit_null_projection["lanes"][identifier]["projectionSpecDigest"] = None
        with self.assertRaisesRegex(MathFlowError, "SHA-256 digest"):
            validate_scheduler_state(explicit_null_projection)


if __name__ == "__main__":
    unittest.main()
