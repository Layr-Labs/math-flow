from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

from math_flow.artifacts import (
    ArtifactBundle,
    load_manifest,
    read_verified_artifact,
    sha256_bytes,
    verify_bundle,
)
from math_flow.cli import main
from math_flow.coordination import lane_id, publish_batch, record_completed_inputs
from math_flow.credit import (
    _credit_schema,
    _validate_credit_index,
    load_credit_assignment_bundle,
    run_credit_assignment_bundle,
)
from math_flow.credit_schedule import (
    filter_credit_dispatch_history,
    next_calendar_allocation_window,
    plan_credit_run,
    plan_due_credit_dispatches,
)
from math_flow.credit_context import build_credit_context
from math_flow.errors import MathFlowError
from math_flow.governance import resolve_projection
from math_flow.knowledge import empty_state_v3
from math_flow.projection_dependencies import (
    resolve_projection_dependencies,
    same_projection_dependency_state,
)
from math_flow.repository import commit_timestamp, ledger, sha256_json
from math_flow.viewer import export_viewer_catalog


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


def projection_spec(
    projection_id: str, dependencies: list[dict[str, str]] | None = None
) -> dict[str, object]:
    value: dict[str, object] = {
        "schemaVersion": 1,
        "id": projection_id,
        "description": f"Projection {projection_id}",
        "status": "active",
        "engine": "openrouter-repository-v1",
        "allowedProblems": ["demo"],
        "primaryJudge": "protocol/judges/primary.json",
        "reconciliationJudge": "protocol/judges/reconciliation.json",
        "knowledgeBuilder": "protocol/judges/builder.json",
        "scheduling": {
            "judgmentMaxParallel": 8,
            "knowledgeMinimumIntervalSeconds": 0,
            "maximumJudgmentsPerBuild": 100,
        },
    }
    if dependencies is not None:
        value["dependencies"] = dependencies
    return value


def overlay_projection_spec(
    dependencies: list[dict[str, str]],
) -> dict[str, object]:
    return {
        "schemaVersion": 2,
        "id": "credit-v1",
        "description": "Credit overlay",
        "status": "active",
        "engine": "overlay-repository-v1",
        "allowedProblems": ["demo"],
        "runner": {
            "implementation": "openrouter-credit-assignment-v1",
            "spec": "protocol/judges/credit.json",
        },
        "dependencies": dependencies,
        "scheduling": {"minimumIntervalSeconds": 0},
    }


class ProjectionDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.projection_root = self.root / "published"
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Dependency Test")
        git(self.root, "config", "user.email", "dependency@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        write(
            self.root / "problems/demo/contributions/first-result/README.md",
            "# First result\n\nA complete proof of the fixture claim.\n",
        )
        for name, implementation in {
            "primary": "openrouter-markdown-judgment-v1",
            "reconciliation": "openrouter-markdown-reconciliation-v1",
            "builder": "openrouter-knowledge-builder-v1",
        }.items():
            write_json(
                self.root / f"protocol/judges/{name}.json",
                {"implementation": implementation},
            )
        write(
            self.root / "protocol/judges/credit.json",
            (
                Path(__file__).parents[1]
                / "protocol/judges/openrouter-credit-assignment-v1.json"
            ).read_text(encoding="utf-8"),
        )
        write_json(
            self.root / "protocol/projections/knowledge-v1.json",
            projection_spec("knowledge-v1"),
        )
        write_json(
            self.root / "protocol/projections/credit-v1.json",
            overlay_projection_spec(
                [
                    {
                        "name": "knowledge",
                        "projectionId": "knowledge-v1",
                        "artifactRole": "knowledge-state",
                    }
                ],
            ),
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Initialize dependency fixture")
        self.head = git(self.root, "rev-parse", "HEAD")
        self._publish_knowledge_state()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _publish_knowledge_state(self) -> None:
        source = ledger(self.root, "demo", self.head)
        producer = resolve_projection(
            self.root, "knowledge-v1", "demo", self.head
        )
        builder = json.loads(
            (self.root / "protocol/judges/builder.json").read_text(
                encoding="utf-8"
            )
        )
        builder_digest = f"sha256:{sha256_json(builder)}"
        projection_digest = str(producer["projectionSpecDigest"])
        identifier = lane_id("demo", builder_digest, projection_digest)

        bundle = self.root / "knowledge-bundle"
        writer = ArtifactBundle(bundle)
        writer.add_json(
            "state/state.json",
            empty_state_v3("demo"),
            "knowledge-state",
        )
        writer.add_text(
            "state/revisions.jsonl",
            "",
            "knowledge-revisions",
            "application/x-ndjson",
        )
        writer.add_text(
            "report.md", "# Knowledge state\n", "report", "text/markdown"
        )
        writer.add_json(
            "control/selection.json",
            {"selectedNodeIds": [], "rationale": "No knowledge revisions."},
            "node-selection",
        )
        writer.add_json(
            "control/normalizations.json",
            {"normalizations": []},
            "adapter-normalizations",
        )
        writer.add_json("state/delta.json", {"operations": []}, "knowledge-delta")
        writer.finalize(
            {
                "protocolVersion": 1,
                "runKind": "knowledge-build",
                "problemId": "demo",
                "ledgerHead": source["ledgerHead"],
                "problemLedgerHead": source["problemLedgerHead"],
                "problemLedgerDigest": source["problemLedgerDigest"],
                "outputProfile": "math-flow/knowledge-build-markdown-v2",
                "judgeSpec": {"id": "builder", "digest": builder_digest},
                "runner": {"implementation": "fixture", "mathFlowVersion": "test"},
                "baseRun": None,
                "providerRuns": [],
                "inputs": {
                    "laneId": identifier,
                    "problemId": "demo",
                    "builderSpecDigest": builder_digest,
                    "projectionSpecDigest": projection_digest,
                },
            }
        )
        _, run_digest = load_manifest(bundle)
        digest_hex = run_digest.removeprefix("sha256:")
        target = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / digest_hex[:2]
            / digest_hex
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bundle, target)
        write_json(
            self.projection_root / "indexes/problems/demo/runs.json",
            [
                {
                    "runDigest": run_digest,
                    "runKind": "knowledge-build",
                    "problemId": "demo",
                    "path": target.relative_to(self.projection_root).as_posix(),
                }
            ],
        )

        scheduler = self.projection_root / "coordination/scheduler.json"
        lane = record_completed_inputs(
            scheduler,
            "demo",
            builder_digest,
            [],
            [],
            0,
            10,
            projection_digest,
        )
        lane["latestStateRun"] = run_digest
        lane["lastCompletedAt"] = 10
        lane["nextEligibleAt"] = None
        state = {
            "schemaVersion": 1,
            "lanes": {identifier: lane},
        }
        write_json(scheduler, state)

    def _publish_credit_assignment(
        self,
        *,
        as_of: int | None = None,
        bundle_name: str = "published-credit-bundle",
    ) -> tuple[Path, str]:
        transaction_id = str(
            ledger(self.root, "demo", self.head)["transactions"][0][
                "transactionId"
            ]
        )
        report = (
            "# Credit assessment\n\n"
            f"## Contribution: {transaction_id}\n\n"
            "This transaction supplies the fixture proof.\n"
        )
        extracted = {
            "assignments": [
                {
                    "transactionId": transaction_id,
                    "significance": "major",
                    "roles": ["proof"],
                    "knowledgeRefs": [
                        {"nodeId": "root", "revisionId": None}
                    ],
                    "reservationTransactionIds": [],
                }
            ]
        }
        calls = 0

        def transport(payload: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            return {
                "id": f"credit-context-{calls}",
                "model": "openai/gpt-5.6-sol",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": report if calls == 1 else json.dumps(extracted),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                },
            }

        bundle = self.root / bundle_name
        run_credit_assignment_bundle(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            bundle,
            transport=transport,
            as_of=as_of,
        )
        batch = publish_batch(self.projection_root, [bundle])
        return bundle, str(batch["objects"][0]["runDigest"])

    def test_resolves_exact_verified_dependency_lock_and_cli(self) -> None:
        first = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )
        second = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )
        self.assertEqual(first, second)
        self.assertRegex(
            first["dependencyLockDigest"], r"^sha256:[0-9a-f]{64}$"
        )
        dependency = first["dependencies"][0]
        self.assertEqual(dependency["name"], "knowledge")
        self.assertEqual(dependency["artifact"]["role"], "knowledge-state")
        self.assertRegex(dependency["runDigest"], r"^sha256:[0-9a-f]{64}$")

        output = self.root / "dependency-lock.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "resolve-projection-dependencies",
                    "--projection",
                    "credit-v1",
                    "--problem",
                    "demo",
                    "--head",
                    self.head,
                    "--projection-dir",
                    str(self.projection_root),
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), first)

    def test_rolling_credit_plan_is_provider_free_and_coalesces_current_state(self) -> None:
        initial = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=123,
        )
        self.assertTrue(initial["eligible"])
        self.assertEqual(initial["schedule"]["mode"], "rolling")
        self.assertIsNone(initial["schedule"]["allocationWindow"])

        due = plan_due_credit_dispatches(
            self.root, self.projection_root, self.head, as_of=123
        )
        self.assertEqual(
            [(item["projectionId"], item["problemId"]) for item in due["dispatches"]],
            [("credit-v1", "demo")],
        )

        self._publish_credit_assignment()
        covered = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=999_999,
        )
        self.assertFalse(covered["eligible"])
        self.assertEqual(
            covered["reasonCode"], "dependency-state-already-covered"
        )
        calls = 0

        def forbidden_transport(_: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            raise AssertionError("ineligible credit run reached its provider")

        with self.assertRaisesRegex(MathFlowError, "not eligible"):
            run_credit_assignment_bundle(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                self.head,
                self.root / "ineligible-credit-run",
                transport=forbidden_transport,
                as_of=999_999,
            )
        self.assertEqual(calls, 0)

    def test_automatic_credit_retry_history_is_semantic_bounded_and_resettable(self) -> None:
        plan = plan_due_credit_dispatches(
            self.root, self.projection_root, self.head, as_of=123
        )
        dispatch = plan["dispatches"][0]
        title = (
            f"Credit {dispatch['projectionId']}/{dispatch['problemId']} "
            f"[{dispatch['automaticRetryKey']}]"
        )

        def run(
            run_id: int,
            *,
            status: str = "completed",
            conclusion: str | None = "failure",
            display_title: str = title,
            head: str = "f" * 40,
        ) -> dict[str, object]:
            return {
                "conclusion": conclusion,
                "databaseId": run_id,
                "displayTitle": display_title,
                "headSha": head,
                "status": status,
            }

        active = filter_credit_dispatch_history(
            plan, [run(1, status="in_progress", conclusion=None)]
        )
        self.assertEqual(active["dispatches"], [])
        capped = filter_credit_dispatch_history(
            plan, [run(index) for index in range(1, 6)]
        )
        self.assertEqual(capped["dispatches"], [])
        non_success_terminal = filter_credit_dispatch_history(
            plan,
            [run(index, conclusion="timed_out") for index in range(1, 6)],
        )
        self.assertEqual(non_success_terminal["dispatches"], [])
        reset = filter_credit_dispatch_history(
            plan,
            [
                *[run(index) for index in range(1, 6)],
                run(6, conclusion="success"),
            ],
        )
        self.assertEqual(reset["dispatches"], [dispatch])
        unrelated = filter_credit_dispatch_history(
            plan,
            [
                run(
                    index,
                    display_title=(
                        f"Credit {dispatch['projectionId']}/{dispatch['problemId']} "
                        f"[sha256:{'0' * 64}]"
                    ),
                )
                for index in range(1, 6)
            ],
        )
        self.assertEqual(unrelated["dispatches"], [dispatch])

    def test_due_credit_planning_isolates_one_overlay_error(self) -> None:
        second = overlay_projection_spec(
            [
                {
                    "name": "knowledge",
                    "projectionId": "knowledge-v1",
                    "artifactRole": "knowledge-state",
                }
            ]
        )
        second["id"] = "credit-second-v1"
        write_json(
            self.root / "protocol/projections/credit-second-v1.json", second
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add a second credit overlay")
        self.head = git(self.root, "rev-parse", "HEAD")
        real_plan = plan_credit_run

        def isolated_plan(
            root: Path,
            projection_root: Path,
            projection: str,
            problem: str,
            head: str,
            as_of: int,
        ) -> dict[str, object]:
            if projection == "credit-v1":
                raise MathFlowError("fixture corrupt credit history")
            return real_plan(
                root, projection_root, projection, problem, head, as_of
            )

        with patch(
            "math_flow.credit_schedule.plan_credit_run",
            side_effect=isolated_plan,
        ):
            plan = plan_due_credit_dispatches(
                self.root, self.projection_root, self.head, as_of=123
            )
        self.assertEqual(
            [item["projectionId"] for item in plan["dispatches"]],
            ["credit-second-v1"],
        )
        self.assertEqual(
            plan["planningErrors"],
            [
                {
                    "problemId": "demo",
                    "projectionId": "credit-v1",
                    "message": "fixture corrupt credit history",
                }
            ],
        )

    def test_daily_credit_plan_scopes_latest_closed_utc_period(self) -> None:
        projection = overlay_projection_spec(
            [
                {
                    "name": "knowledge",
                    "projectionId": "knowledge-v1",
                    "artifactRole": "knowledge-state",
                }
            ]
        )
        projection["scheduling"]["utcCalendarPeriod"] = {"unit": "day"}
        write_json(
            self.root / "protocol/projections/credit-v1.json", projection
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Use daily credit allocation windows")
        self.head = git(self.root, "rev-parse", "HEAD")

        transaction_id = str(
            ledger(self.root, "demo", self.head)["transactions"][0]["transactionId"]
        )
        transaction_time = commit_timestamp(self.root, transaction_id)
        period_end = ((transaction_time // 86_400) + 1) * 86_400
        as_of = period_end + 60
        plan = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=as_of,
        )
        self.assertTrue(plan["eligible"])
        self.assertEqual(
            plan["schedule"]["allocationWindow"],
            {
                "unit": "day",
                "startAt": period_end - 86_400,
                "endAt": period_end,
                "transactionIds": [transaction_id],
            },
        )

        report = (
            "# Daily credit\n\n"
            f"## Contribution: {transaction_id}\n\n"
            "This contribution is in the governed daily allocation window.\n"
        )
        extracted = {
            "assignments": [
                {
                    "transactionId": transaction_id,
                    "significance": "major",
                    "roles": ["proof"],
                    "knowledgeRefs": [{"nodeId": "root", "revisionId": None}],
                    "reservationTransactionIds": [],
                }
            ]
        }
        calls = 0
        requests: list[dict[str, object]] = []

        def transport(payload: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            requests.append(payload)
            return {
                "id": f"daily-credit-{calls}",
                "model": "openai/gpt-5.6-sol",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": report if calls == 1 else json.dumps(extracted),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 10,
                    "total_tokens": 20,
                },
            }

        bundle = self.root / "daily-credit-run"
        manifest = run_credit_assignment_bundle(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            bundle,
            transport=transport,
            as_of=as_of,
        )
        self.assertEqual(manifest["inputs"]["schedule"], plan["schedule"])
        report_prompt = str(requests[0]["messages"][-1]["content"])
        self.assertNotIn("every canonical contribution", report_prompt)
        self.assertIn("governed UTC allocation window", report_prompt)
        publish_batch(self.projection_root, [bundle])
        covered = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=as_of,
        )
        self.assertEqual(covered["reasonCode"], "no-new-closed-calendar-period")
        empty = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=period_end + 86_400 + 60,
        )
        self.assertEqual(empty["reasonCode"], "calendar-periods-empty")

    def test_calendar_chain_catches_up_earliest_nonempty_closed_period(self) -> None:
        transactions = [
            {"transactionId": "1" * 40},
            {"transactionId": "2" * 40},
            {"transactionId": "3" * 40},
        ]
        timestamps = {
            "1" * 40: 100,
            "2" * 40: 2 * 86_400 + 100,
            "3" * 40: 3 * 86_400 + 100,
        }
        with patch(
            "math_flow.credit_schedule.commit_timestamp",
            side_effect=lambda _root, transaction_id: timestamps[transaction_id],
        ):
            window = next_calendar_allocation_window(
                self.root,
                transactions,
                "day",
                latest_closed_end=4 * 86_400,
                previous_end=86_400,
            )
            following = next_calendar_allocation_window(
                self.root,
                transactions,
                "day",
                latest_closed_end=4 * 86_400,
                previous_end=3 * 86_400,
            )
        self.assertEqual(
            window,
            {
                "unit": "day",
                "startAt": 2 * 86_400,
                "endAt": 3 * 86_400,
                "transactionIds": ["2" * 40],
            },
        )
        self.assertEqual(
            following,
            {
                "unit": "day",
                "startAt": 3 * 86_400,
                "endAt": 4 * 86_400,
                "transactionIds": ["3" * 40],
            },
        )

    def test_calendar_assignment_scope_allows_prior_ledger_reservations(self) -> None:
        prior = "1" * 40
        current = "2" * 40
        schema = _credit_schema(
            [current],
            {"root": None},
            reservation_transaction_ids=[prior, current],
        )
        assignment_schema = schema["properties"]["assignments"]["items"]
        self.assertEqual(
            assignment_schema["properties"]["transactionId"]["enum"],
            [current],
        )
        self.assertEqual(
            assignment_schema["properties"]["reservationTransactionIds"]
            ["items"]["enum"],
            [prior, current],
        )
        result = _validate_credit_index(
            {
                "assignments": [
                    {
                        "transactionId": current,
                        "significance": "major",
                        "roles": ["proof"],
                        "knowledgeRefs": [
                            {"nodeId": "root", "revisionId": None}
                        ],
                        "reservationTransactionIds": [prior],
                    }
                ]
            },
            "demo",
            "sha256:" + "a" * 64,
            [
                {"transactionId": prior, "ordinal": 1},
                {"transactionId": current, "ordinal": 2},
            ],
            {"root": None},
            f"## Contribution: {current}\n\nWindow-scoped credit.\n",
            assignment_transaction_ids=[current],
        )
        self.assertEqual(
            result["assignments"][0]["reservationTransactionIds"], [prior]
        )

    def test_rolling_minimum_interval_coalesces_a_changed_dependency(self) -> None:
        projection = overlay_projection_spec(
            [
                {
                    "name": "knowledge",
                    "projectionId": "knowledge-v1",
                    "artifactRole": "knowledge-state",
                }
            ]
        )
        projection["scheduling"]["minimumIntervalSeconds"] = 60
        write_json(
            self.root / "protocol/projections/credit-v1.json", projection
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Coalesce credit for one minute")
        self.head = git(self.root, "rev-parse", "HEAD")
        _, first_credit = self._publish_credit_assignment(as_of=100)

        scheduler_path = self.projection_root / "coordination/scheduler.json"
        scheduler = json.loads(scheduler_path.read_text(encoding="utf-8"))
        lane = next(iter(scheduler["lanes"].values()))
        old_digest = str(lane["latestStateRun"])
        old_hex = old_digest.removeprefix("sha256:")
        old_bundle = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / old_hex[:2]
            / old_hex
        )
        advanced = self.root / "advanced-knowledge-bundle"
        shutil.copytree(old_bundle, advanced)
        run = json.loads((advanced / "run.json").read_text(encoding="utf-8"))
        run["baseRun"] = old_digest
        run["inputs"]["testGeneration"] = 2
        write_json(advanced / "run.json", run)
        _, advanced_digest = load_manifest(advanced)
        advanced_hex = advanced_digest.removeprefix("sha256:")
        target = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / advanced_hex[:2]
            / advanced_hex
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(advanced, target)
        index_path = self.projection_root / "indexes/problems/demo/runs.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index.append(
            {
                "runDigest": advanced_digest,
                "runKind": "knowledge-build",
                "problemId": "demo",
                "path": target.relative_to(self.projection_root).as_posix(),
            }
        )
        write_json(index_path, index)
        lane["latestStateRun"] = advanced_digest
        lane["lastCompletedAt"] = 20
        write_json(scheduler_path, scheduler)

        waiting = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=159,
        )
        self.assertFalse(waiting["eligible"])
        self.assertEqual(waiting["reasonCode"], "minimum-interval-not-elapsed")
        self.assertEqual(waiting["nextEligibleAt"], 160)
        due = plan_credit_run(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            as_of=160,
        )
        self.assertTrue(due["eligible"])
        self.assertEqual(due["schedule"]["previousRunDigest"], first_credit)
        _, second_credit = self._publish_credit_assignment(
            as_of=160, bundle_name="second-published-credit-bundle"
        )
        catalog = export_viewer_catalog(
            self.root,
            self.projection_root,
            "example/math-flow",
            canonical_ref="HEAD",
        )
        overlay = catalog["creditProjections"][0]
        self.assertEqual(overlay["runCount"], 2)
        self.assertEqual(overlay["selectionStatus"], "current")
        self.assertEqual(overlay["latestRunDigest"], second_credit)
        current_context, _ = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            self.head,
            list(ledger(self.root, "demo", self.head)["transactions"]),
        )
        self.assertEqual(current_context["status"], "current")
        self.assertEqual(current_context["run"]["runDigest"], second_credit)
        projection["scheduling"]["minimumIntervalSeconds"] = 61
        write_json(
            self.root / "protocol/projections/credit-v1.json", projection
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Revise the governed credit cadence")
        self.head = git(self.root, "rev-parse", "HEAD")
        stale_context, _ = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            self.head,
            list(ledger(self.root, "demo", self.head)["transactions"]),
        )
        self.assertEqual(stale_context["status"], "stale")
        self.assertEqual(stale_context["run"]["runDigest"], second_credit)

    def test_catalog_exposes_admitted_credit_projection_before_first_run(self) -> None:
        catalog = export_viewer_catalog(
            self.root,
            self.projection_root,
            "example/math-flow",
            canonical_ref="HEAD",
        )
        self.assertEqual(len(catalog["creditProjections"]), 1)
        credit = catalog["creditProjections"][0]
        self.assertEqual(credit["id"], "credit-v1")
        self.assertEqual(credit["knowledgeProjectionIds"], ["knowledge-v1"])
        self.assertIsNone(credit["latestRunDigest"])
        self.assertEqual(credit["selectionStatus"], "pending")
        self.assertEqual(credit["runCount"], 0)
        self.assertEqual(credit["runs"], [])

    def test_dependency_state_comparison_ignores_only_consumer_audit_head(self) -> None:
        lock = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )

        def revised(
            mutator: Callable[[dict[str, object]], None]
        ) -> dict[str, object]:
            value = copy.deepcopy(lock)
            mutator(value)
            core = {
                key: item
                for key, item in value.items()
                if key != "dependencyLockDigest"
            }
            value["dependencyLockDigest"] = f"sha256:{sha256_json(core)}"
            return value

        unrelated_head = revised(
            lambda value: value["consumer"].__setitem__(
                "canonicalHead", "f" * 40
            )
        )
        changed_projection = revised(
            lambda value: value["consumer"].__setitem__(
                "projectionSpecDigest", "sha256:" + "a" * 64
            )
        )
        changed_problem = revised(
            lambda value: value["problemLedger"].__setitem__(
                "problemLedgerDigest", "sha256:" + "b" * 64
            )
        )
        changed_dependency = revised(
            lambda value: value["dependencies"][0].__setitem__(
                "runDigest", "sha256:" + "c" * 64
            )
        )

        self.assertTrue(same_projection_dependency_state(lock, unrelated_head))
        self.assertFalse(
            same_projection_dependency_state(lock, changed_projection)
        )
        self.assertFalse(same_projection_dependency_state(lock, changed_problem))
        self.assertFalse(
            same_projection_dependency_state(lock, changed_dependency)
        )
        invalid = copy.deepcopy(lock)
        invalid["consumer"]["canonicalHead"] = "e" * 40
        self.assertFalse(same_projection_dependency_state(lock, invalid))

    def test_rejects_stale_or_unfinished_dependency(self) -> None:
        write(
            self.root / "problems/demo/contributions/new-result/README.md",
            "# New result\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Advance demo ledger")
        new_head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "is stale"):
            resolve_projection_dependencies(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                new_head,
            )

        state_path = self.projection_root / "coordination/scheduler.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        lane = next(iter(state["lanes"].values()))
        pending = "sha256:" + "1" * 64
        lane["observedJudgmentIds"] = [pending]
        lane["pendingJudgmentIds"] = [pending]
        lane["nextEligibleAt"] = 10
        write_json(state_path, state)
        with self.assertRaisesRegex(MathFlowError, "pending knowledge inputs"):
            resolve_projection_dependencies(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                self.head,
            )

    def test_rejects_unsupported_dependency_role_before_execution(self) -> None:
        consumer = overlay_projection_spec(
            [
                {
                    "name": "judgments",
                    "projectionId": "knowledge-v1",
                    "artifactRole": "judgment-record",
                }
            ],
        )
        write_json(
            self.root / "protocol/projections/credit-v1.json", consumer
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Request unsupported dependency role")
        head = git(self.root, "rev-parse", "HEAD")

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = main(
                [
                    "--root",
                    str(self.root),
                    "resolve-projection-dependencies",
                    "--projection",
                    "credit-v1",
                    "--problem",
                    "demo",
                    "--head",
                    head,
                    "--projection-dir",
                    str(self.projection_root),
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("role is not supported", stderr.getvalue())

    def test_rejects_dependency_run_with_the_wrong_builder_identity(self) -> None:
        scheduler_path = self.projection_root / "coordination/scheduler.json"
        scheduler = json.loads(scheduler_path.read_text(encoding="utf-8"))
        lane = next(iter(scheduler["lanes"].values()))
        prior_digest = str(lane["latestStateRun"])
        prior_hex = prior_digest.removeprefix("sha256:")
        prior = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / prior_hex[:2]
            / prior_hex
        )
        manifest = json.loads((prior / "run.json").read_text(encoding="utf-8"))
        manifest["judgeSpec"]["digest"] = "sha256:" + "f" * 64
        rendered = json.dumps(manifest, indent=2) + "\n"
        bad_digest = sha256_bytes(rendered.encode("utf-8"))
        bad_hex = bad_digest.removeprefix("sha256:")
        bad = (
            self.projection_root
            / "objects"
            / "knowledge-build"
            / bad_hex[:2]
            / bad_hex
        )
        bad.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(prior, bad)
        write(bad / "run.json", rendered)
        lane["latestStateRun"] = bad_digest
        write_json(scheduler_path, scheduler)

        with self.assertRaisesRegex(MathFlowError, "does not match 'knowledge-v1'"):
            resolve_projection_dependencies(
                self.root,
                self.projection_root,
                "credit-v1",
                "demo",
                self.head,
            )

    def test_credit_runner_keeps_reasoning_in_markdown_and_indexes_transactions(self) -> None:
        transaction_id = str(
            ledger(self.root, "demo", self.head)["transactions"][0][
                "transactionId"
            ]
        )
        report = "\n".join(
            [
                "# Credit assessment",
                "",
                f"## Contribution: {transaction_id}",
                "",
                "This transaction supplies the complete proof represented by the locked root state.",
                "",
            ]
        )
        extracted = {
            "assignments": [
                {
                    "transactionId": transaction_id,
                    "significance": "major",
                    "roles": ["proof"],
                    "knowledgeRefs": [
                        {"nodeId": "root", "revisionId": None}
                    ],
                    "reservationTransactionIds": [],
                }
            ]
        }
        requests: list[dict[str, object]] = []

        def transport(payload: dict[str, object]) -> dict[str, object]:
            requests.append(payload)
            content = report if len(requests) == 1 else json.dumps(extracted)
            return {
                "id": f"credit-{len(requests)}",
                "model": "openai/gpt-5.6-sol",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                },
            }

        output = self.root / "credit-run"
        manifest = run_credit_assignment_bundle(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
            output,
            transport=transport,
        )
        self.assertEqual(len(requests), 2)
        self.assertNotIn("response_format", requests[0])
        self.assertIn("response_format", requests[1])
        self.assertNotIn(
            '"reportSection"', json.dumps(requests[1]["response_format"])
        )
        self.assertEqual(manifest["runKind"], "credit-assignment")
        self.assertEqual(manifest["baseRun"], None)
        self.assertEqual(
            manifest["outputProfile"],
            "math-flow/credit-assignment-markdown-v1",
        )
        verified, run_digest = verify_bundle(output)
        self.assertEqual(verified, manifest)
        self.assertRegex(run_digest, r"^sha256:[0-9a-f]{64}$")
        loaded_manifest, loaded_index, loaded_digest = (
            load_credit_assignment_bundle(output)
        )
        self.assertEqual(loaded_manifest, manifest)
        self.assertEqual(loaded_digest, run_digest)
        index = json.loads(
            read_verified_artifact(output, manifest, "credit-index")
        )
        self.assertEqual(
            index["assignments"],
            [
                {
                    **extracted["assignments"][0],
                    "reportSection": f"## Contribution: {transaction_id}",
                }
            ],
        )
        self.assertEqual(loaded_index, index)
        lock = json.loads(
            read_verified_artifact(output, manifest, "dependency-lock")
        )
        self.assertEqual(
            index["dependencyLockDigest"], lock["dependencyLockDigest"]
        )
        publish_batch(self.projection_root, [output])
        write(self.root / "docs/viewer-note.md", "Unrelated viewer documentation.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add unrelated viewer documentation")
        self.assertNotEqual(git(self.root, "rev-parse", "HEAD"), self.head)
        with patch(
            "math_flow.viewer.load_credit_assignment_bundle",
            wraps=load_credit_assignment_bundle,
        ) as load_credit:
            catalog = export_viewer_catalog(
                self.root,
                self.projection_root,
                "example/math-flow",
                canonical_ref="HEAD",
            )
        load_credit.assert_called_once()
        credit = catalog["creditProjections"][0]
        self.assertEqual(credit["latestRunDigest"], run_digest)
        self.assertEqual(credit["runCount"], 1)
        viewer_run = credit["runs"][0]
        self.assertFalse(viewer_run["stale"])
        self.assertEqual(viewer_run["staleReasons"], [])
        self.assertEqual(viewer_run["assignments"], index["assignments"])
        self.assertEqual(viewer_run["reportMarkdown"], report)
        self.assertEqual(
            viewer_run["dependency"]["runDigest"],
            lock["dependencies"][0]["runDigest"],
        )
        self.assertEqual(
            viewer_run["creditInput"]["dependencyLockDigest"],
            lock["dependencyLockDigest"],
        )
        self.assertEqual(credit["selectionStatus"], "current")

    def test_publisher_refuses_an_arbitrary_scheduled_credit_terminal(self) -> None:
        first_bundle, first_digest = self._publish_credit_assignment()
        second_bundle = self.root / "second-credit-bundle"
        shutil.copytree(first_bundle, second_bundle)
        second_manifest = json.loads(
            (second_bundle / "run.json").read_text(encoding="utf-8")
        )
        second_manifest["providerRuns"][0]["responseId"] = "independent-rerun"
        write_json(second_bundle / "run.json", second_manifest)
        with self.assertRaisesRegex(MathFlowError, "previousRunDigest"):
            publish_batch(self.projection_root, [second_bundle])

        catalog = export_viewer_catalog(
            self.root,
            self.projection_root,
            "example/math-flow",
            canonical_ref="HEAD",
        )
        credit = catalog["creditProjections"][0]
        self.assertEqual(credit["runCount"], 1)
        self.assertEqual(credit["selectionStatus"], "current")
        self.assertEqual(credit["latestRunDigest"], first_digest)

        source = ledger(self.root, "demo", self.head)
        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            self.head,
            list(source["transactions"]),
        )
        self.assertEqual(context["status"], "current")
        self.assertEqual(context["run"]["runDigest"], first_digest)
        self.assertIsNotNone(report)

    def test_agent_credit_context_selects_unique_current_verified_run(self) -> None:
        _, run_digest = self._publish_credit_assignment()
        source = ledger(self.root, "demo", self.head)
        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            self.head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "current")
        self.assertEqual(context["run"]["runDigest"], run_digest)
        self.assertTrue(context["run"]["authoritative"])
        self.assertEqual(context["assignments"][0]["significance"], "major")
        self.assertEqual(context["assignments"][0]["roles"], ["proof"])
        self.assertIn("fixture proof", report)
        self.assertEqual(context["dependency"]["status"], "current")

    def test_agent_credit_context_survives_unrelated_canonical_commit(self) -> None:
        _, run_digest = self._publish_credit_assignment()
        write(self.root / "docs/unrelated.md", "# Unrelated documentation\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Document unrelated behavior")
        later_head = git(self.root, "rev-parse", "HEAD")
        source = ledger(self.root, "demo", later_head)

        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            later_head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "current")
        self.assertEqual(context["run"]["runDigest"], run_digest)
        self.assertTrue(context["run"]["authoritative"])
        self.assertNotEqual(
            context["dependency"]["lockDigest"],
            context["run"]["dependencyLockDigest"],
        )
        self.assertEqual(
            context["dependency"]["consumer"]["canonicalHead"], later_head
        )
        self.assertEqual(
            context["run"]["dependencyConsumer"]["canonicalHead"], self.head
        )
        self.assertIsNotNone(report)

    def test_agent_credit_context_stales_after_consumer_projection_change(self) -> None:
        self._publish_credit_assignment()
        projection_path = self.root / "protocol/projections/credit-v1.json"
        projection = json.loads(projection_path.read_text(encoding="utf-8"))
        projection["scheduling"]["minimumIntervalSeconds"] = 1
        write_json(projection_path, projection)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Revise credit projection")
        later_head = git(self.root, "rev-parse", "HEAD")
        source = ledger(self.root, "demo", later_head)

        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            later_head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "stale")
        self.assertFalse(context["run"]["authoritative"])
        self.assertIsNotNone(report)

    def test_agent_credit_context_reports_governed_projection_without_run(self) -> None:
        source = ledger(self.root, "demo", self.head)
        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            self.head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "pending")
        self.assertEqual(context["reasonCode"], "no-published-credit-run")
        self.assertEqual(context["dependency"]["status"], "current")
        self.assertNotIn("run", context)
        self.assertNotIn("assignments", context)
        self.assertIsNone(report)

    def test_agent_credit_context_marks_historical_run_stale(self) -> None:
        self._publish_credit_assignment()
        write(
            self.root / "problems/demo/contributions/later/README.md",
            "# Later evidence\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add later evidence")
        later_head = git(self.root, "rev-parse", "HEAD")
        source = ledger(self.root, "demo", later_head)

        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            later_head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "stale")
        self.assertEqual(context["dependency"]["status"], "stale")
        self.assertFalse(context["run"]["authoritative"])
        self.assertIsNotNone(report)

    def test_agent_credit_context_reports_invalid_published_run(self) -> None:
        _, run_digest = self._publish_credit_assignment()
        digest_hex = run_digest.removeprefix("sha256:")
        report = (
            self.projection_root
            / "objects"
            / "credit-assignment"
            / digest_hex[:2]
            / digest_hex
            / "report.md"
        )
        report.write_text("tampered\n", encoding="utf-8")
        source = ledger(self.root, "demo", self.head)

        context, selected_report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            self.head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "invalid")
        self.assertIsNone(selected_report)
        self.assertEqual(
            len(context["verification"]["invalidPublishedRuns"]), 1
        )

    def test_agent_credit_context_requires_selection_for_multiple_overlays(self) -> None:
        second = overlay_projection_spec(
            [
                {
                    "name": "knowledge",
                    "projectionId": "knowledge-v1",
                    "artifactRole": "knowledge-state",
                }
            ]
        )
        second["id"] = "credit-second-v1"
        write_json(
            self.root / "protocol/projections/credit-second-v1.json", second
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add second credit overlay")
        head = git(self.root, "rev-parse", "HEAD")
        source = ledger(self.root, "demo", head)

        context, report = build_credit_context(
            self.root,
            self.projection_root,
            "demo",
            head,
            list(source["transactions"]),
        )

        self.assertEqual(context["status"], "selection-required")
        self.assertEqual(
            context["availableProjectionIds"],
            ["credit-second-v1", "credit-v1"],
        )
        self.assertIsNone(report)

    def test_publisher_accepts_credit_assignment_as_an_independent_run_kind(self) -> None:
        transaction_id = str(
            ledger(self.root, "demo", self.head)["transactions"][0][
                "transactionId"
            ]
        )
        dependency_lock = resolve_projection_dependencies(
            self.root,
            self.projection_root,
            "credit-v1",
            "demo",
            self.head,
        )
        bundle = self.root / "credit-bundle"
        writer = ArtifactBundle(bundle)
        writer.add_json(
            "control/dependencies.json", dependency_lock, "dependency-lock"
        )
        writer.add_text(
            "report.md",
            "# Credit assessment\n\n"
            f"## Contribution: {transaction_id}\n\n"
            "No credit assessment was made by this transport fixture.\n",
            "credit-report",
            "text/markdown",
        )
        writer.add_json(
            "credit/index.json",
            {
                "schemaVersion": 1,
                "problemId": "demo",
                "dependencyLockDigest": dependency_lock[
                    "dependencyLockDigest"
                ],
                "assignments": [
                    {
                        "transactionId": transaction_id,
                        "significance": "uncertain",
                        "roles": [],
                        "knowledgeRefs": [],
                        "reservationTransactionIds": [],
                        "reportSection": f"## Contribution: {transaction_id}",
                    }
                ],
            },
            "credit-index",
        )
        source = ledger(self.root, "demo", self.head)
        writer.finalize(
            {
                "protocolVersion": 1,
                "runKind": "credit-assignment",
                "problemId": "demo",
                "ledgerHead": source["ledgerHead"],
                "problemLedgerHead": source["problemLedgerHead"],
                "problemLedgerDigest": source["problemLedgerDigest"],
                "judgeSpec": {
                    "id": "credit-fixture",
                    "digest": "sha256:" + "2" * 64,
                },
                "runner": {
                    "implementation": "credit-fixture-v1",
                    "mathFlowVersion": "0.5.0",
                },
                "judgeBuilder": {
                    "inputBuilder": "credit-input-fixture-v1",
                    "invocationAdapter": "none",
                    "outputAdapter": "credit-index-fixture-v1",
                    "reducer": None,
                },
                "baseRun": None,
                "outputProfile": "math-flow/credit-assignment-markdown-v1",
                "requestDigests": [],
                "providerRuns": [],
                "inputs": {
                    "dependencyLockDigest": dependency_lock[
                        "dependencyLockDigest"
                    ]
                },
            }
        )

        publication = self.root / "credit-publication"
        batch = publish_batch(publication, [bundle])
        self.assertEqual(batch["objects"][0]["runKind"], "credit-assignment")
        self.assertIn(
            "/credit-assignment/",
            "/" + batch["objects"][0]["path"],
        )


if __name__ == "__main__":
    unittest.main()
