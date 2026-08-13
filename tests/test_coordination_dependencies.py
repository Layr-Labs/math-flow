from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from math_flow.coordination import (
    claim_due_build,
    complete_build,
    fail_build,
    load_scheduler,
    record_completed_inputs,
)
from math_flow.errors import MathFlowError


def digest(number: int) -> str:
    return f"sha256:{number:064x}"


class CoordinationDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.scheduler = Path(self.temporary.name) / "scheduler.json"
        self.builder = digest(100)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def record(
        self,
        judgments: list[str],
        conflicts: list[str],
        *,
        now: int,
        conflict_dependencies: dict[str, list[str]] | None = None,
        reconciliation_dependencies: dict[str, dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return record_completed_inputs(
            self.scheduler,
            "demo",
            self.builder,
            judgments,
            conflicts,
            minimum_interval_seconds=0,
            now=now,
            conflict_dependencies=conflict_dependencies,
            reconciliation_dependencies=reconciliation_dependencies,
        )

    def complete(self, lane: dict[str, object], claim: dict[str, object], now: int) -> None:
        complete_build(
            self.scheduler,
            str(lane["laneId"]),
            str(claim["buildToken"]),
            digest(1000 + now),
            now,
        )

    def test_governed_lane_rejects_in_place_builder_digest_change(self) -> None:
        projection = digest(200)
        record_completed_inputs(
            self.scheduler,
            "demo",
            self.builder,
            [digest(1)],
            [],
            minimum_interval_seconds=0,
            now=1,
            projection_spec_digest=projection,
        )
        with self.assertRaisesRegex(
            MathFlowError, "builder digest changed without a new projection identity"
        ):
            record_completed_inputs(
                self.scheduler,
                "demo",
                digest(101),
                [digest(1)],
                [],
                minimum_interval_seconds=0,
                now=2,
                projection_spec_digest=projection,
            )

    def test_incremental_conflict_and_reconciliation_are_claimed_atomically(self) -> None:
        primary_one = digest(1)
        primary_two = digest(2)
        conflict = digest(3)
        reconciliation = digest(4)

        lane = self.record([primary_one], [], now=10)
        first = claim_due_build(self.scheduler, str(lane["laneId"]), 10, 1)
        self.assertIsNotNone(first)
        self.assertEqual(first["judgmentIds"], [primary_one])
        self.complete(lane, first, 11)

        lane = self.record(
            [primary_one, primary_two],
            [conflict],
            now=20,
            conflict_dependencies={conflict: [primary_two, primary_one]},
            reconciliation_dependencies={},
        )
        self.assertEqual(
            lane["conflictDependencies"],
            {conflict: [primary_one, primary_two]},
        )
        second = claim_due_build(self.scheduler, str(lane["laneId"]), 20, 2)
        self.assertIsNotNone(second)
        self.assertEqual(second["judgmentIds"], [primary_one, primary_two])
        self.assertEqual(second["conflictIds"], [conflict])
        self.complete(lane, second, 21)

        lane = self.record(
            [primary_one, primary_two, reconciliation],
            [conflict],
            now=30,
            conflict_dependencies={conflict: [primary_one, primary_two]},
            reconciliation_dependencies={
                reconciliation: {
                    "conflictId": conflict,
                    "inputJudgmentIds": [primary_two, primary_one],
                }
            },
        )
        self.assertEqual(
            lane["reconciliationDependencies"],
            {
                reconciliation: {
                    "conflictId": conflict,
                    "inputJudgmentIds": [primary_one, primary_two],
                }
            },
        )
        third = claim_due_build(self.scheduler, str(lane["laneId"]), 30, 3)
        self.assertIsNotNone(third)
        self.assertEqual(
            third["judgmentIds"],
            [primary_one, primary_two, reconciliation],
        )
        self.assertEqual(third["conflictIds"], [conflict])

    def test_overlapping_new_conflict_does_not_reclaim_completed_history(self) -> None:
        primary_one = digest(1)
        primary_two = digest(2)
        primary_three = digest(3)
        first_conflict = digest(4)
        second_conflict = digest(5)
        lane = self.record(
            [primary_one, primary_two],
            [first_conflict],
            now=10,
            conflict_dependencies={
                first_conflict: [primary_one, primary_two]
            },
            reconciliation_dependencies={},
        )
        first = claim_due_build(self.scheduler, str(lane["laneId"]), 10, 2)
        self.assertIsNotNone(first)
        self.assertEqual(first["judgmentIds"], [primary_one, primary_two])
        self.assertEqual(first["conflictIds"], [first_conflict])
        self.complete(lane, first, 11)

        lane = self.record(
            [primary_one, primary_two, primary_three],
            [second_conflict],
            now=20,
            conflict_dependencies={
                second_conflict: [primary_one, primary_three]
            },
            reconciliation_dependencies={},
        )
        self.assertEqual(
            lane["pendingJudgmentIds"], [primary_one, primary_three]
        )
        self.assertEqual(lane["pendingConflictIds"], [second_conflict])
        self.assertEqual(
            set(lane["conflictDependencies"]),
            {first_conflict, second_conflict},
        )

        second = claim_due_build(self.scheduler, str(lane["laneId"]), 20, 2)
        self.assertIsNotNone(second)
        self.assertEqual(second["judgmentIds"], [primary_one, primary_three])
        self.assertEqual(second["conflictIds"], [second_conflict])
        self.assertNotIn(primary_two, second["judgmentIds"])
        self.assertNotIn(first_conflict, second["conflictIds"])

    def test_claim_selects_whole_components_and_leaves_others_pending(self) -> None:
        primary_one = digest(1)
        primary_two = digest(2)
        conflict = digest(3)
        independent = digest(15)
        lane = self.record(
            [primary_one, primary_two, independent],
            [conflict],
            now=10,
            conflict_dependencies={conflict: [primary_one, primary_two]},
            reconciliation_dependencies={},
        )

        claim = claim_due_build(self.scheduler, str(lane["laneId"]), 10, 2)
        self.assertIsNotNone(claim)
        self.assertEqual(claim["judgmentIds"], [primary_one, primary_two])
        self.assertEqual(claim["conflictIds"], [conflict])
        stored = load_scheduler(self.scheduler)["lanes"][str(lane["laneId"])]
        self.assertEqual(stored["pendingJudgmentIds"], [independent])
        self.assertEqual(stored["pendingConflictIds"], [])

        self.complete(lane, claim, 11)
        final = claim_due_build(self.scheduler, str(lane["laneId"]), 11, 2)
        self.assertIsNotNone(final)
        self.assertEqual(final["judgmentIds"], [independent])
        self.assertEqual(final["conflictIds"], [])

    def test_maximum_one_handles_independent_work_and_failed_claims(self) -> None:
        first_id = digest(1)
        second_id = digest(2)
        lane = self.record([second_id, first_id], [], now=10)
        self.assertNotIn("conflictDependencies", lane)
        self.assertNotIn("reconciliationDependencies", lane)

        first = claim_due_build(self.scheduler, str(lane["laneId"]), 10, 1)
        self.assertIsNotNone(first)
        self.assertEqual(first["judgmentIds"], [first_id])
        failed = fail_build(
            self.scheduler,
            str(lane["laneId"]),
            str(first["buildToken"]),
            11,
        )
        self.assertEqual(failed["pendingJudgmentIds"], [first_id, second_id])
        self.assertIsNone(
            claim_due_build(self.scheduler, str(lane["laneId"]), 310, 1)
        )
        retry = claim_due_build(self.scheduler, str(lane["laneId"]), 311, 1)
        self.assertIsNotNone(retry)
        self.assertEqual(retry["judgmentIds"], [first_id])
        self.assertEqual(retry["buildToken"], first["buildToken"])
        self.complete(lane, retry, 312)

        second = claim_due_build(self.scheduler, str(lane["laneId"]), 312, 1)
        self.assertIsNotNone(second)
        self.assertEqual(second["judgmentIds"], [second_id])

    def test_failure_backoff_is_durable_and_new_inputs_reset_it(self) -> None:
        first_id = digest(1)
        ledger_digest = digest(900)
        lane = self.record([first_id], [], now=10)
        claim = claim_due_build(self.scheduler, str(lane["laneId"]), 10, 1)
        failed = fail_build(
            self.scheduler,
            str(lane["laneId"]),
            str(claim["buildToken"]),
            10,
            ledger_digest,
        )
        self.assertEqual(failed["nextEligibleAt"], 310)
        self.assertEqual(failed["lastFailure"]["consecutiveFailures"], 1)
        self.assertEqual(
            failed["lastFailure"]["problemLedgerDigest"], ledger_digest
        )

        retry = claim_due_build(self.scheduler, str(lane["laneId"]), 310, 1)
        failed_again = fail_build(
            self.scheduler,
            str(lane["laneId"]),
            str(retry["buildToken"]),
            310,
            ledger_digest,
        )
        self.assertEqual(failed_again["nextEligibleAt"], 910)
        self.assertEqual(
            failed_again["lastFailure"]["consecutiveFailures"], 2
        )

        second_id = digest(2)
        reset = self.record([first_id, second_id], [], now=400)
        self.assertNotIn("lastFailure", reset)
        self.assertEqual(reset["nextEligibleAt"], 400)

    def test_legacy_lane_is_accepted_until_dependency_bearing_work_is_pending(self) -> None:
        primary = digest(1)
        conflict = digest(2)
        lane = self.record([primary], [], now=10)
        claim = claim_due_build(self.scheduler, str(lane["laneId"]), 10, 1)
        self.assertIsNotNone(claim)
        self.complete(lane, claim, 11)

        lane = self.record([], [conflict], now=20)
        with self.assertRaisesRegex(
            MathFlowError,
            "pending conflict has no persisted primary-judgment dependencies",
        ):
            claim_due_build(self.scheduler, str(lane["laneId"]), 20, 1)

    def test_dependency_component_larger_than_policy_is_not_claimed(self) -> None:
        primary_one = digest(1)
        primary_two = digest(2)
        conflict = digest(3)
        lane = self.record(
            [primary_one, primary_two],
            [conflict],
            now=10,
            conflict_dependencies={conflict: [primary_one, primary_two]},
            reconciliation_dependencies={},
        )

        with self.assertRaisesRegex(
            MathFlowError,
            "dependency component exceeds maximum judgments per build \\(2 > 1\\)",
        ):
            claim_due_build(self.scheduler, str(lane["laneId"]), 10, 1)
        stored = load_scheduler(self.scheduler)["lanes"][str(lane["laneId"])]
        self.assertIsNone(stored["activeBuild"])
        self.assertEqual(
            stored["pendingJudgmentIds"], [primary_one, primary_two]
        )
        self.assertEqual(stored["pendingConflictIds"], [conflict])

    def test_content_addressed_dependency_records_cannot_drift(self) -> None:
        primary_one = digest(1)
        primary_two = digest(2)
        replacement_primary = digest(5)
        conflict = digest(3)
        replacement_conflict = digest(6)
        reconciliation = digest(4)
        lane = self.record(
            [primary_one, primary_two, reconciliation],
            [conflict],
            now=10,
            conflict_dependencies={conflict: [primary_one, primary_two]},
            reconciliation_dependencies={
                reconciliation: {
                    "conflictId": conflict,
                    "inputJudgmentIds": [primary_one, primary_two],
                }
            },
        )

        with self.assertRaisesRegex(
            MathFlowError, "conflict dependency changed for content-addressed ID"
        ):
            self.record(
                [primary_one, replacement_primary],
                [conflict],
                now=20,
                conflict_dependencies={
                    conflict: [primary_one, replacement_primary]
                },
                reconciliation_dependencies={},
            )
        with self.assertRaisesRegex(
            MathFlowError,
            "reconciliation dependency changed for content-addressed ID",
        ):
            self.record(
                [primary_one, primary_two, reconciliation],
                [replacement_conflict],
                now=20,
                conflict_dependencies={
                    replacement_conflict: [primary_one, primary_two]
                },
                reconciliation_dependencies={
                    reconciliation: {
                        "conflictId": replacement_conflict,
                        "inputJudgmentIds": [primary_one, primary_two],
                    }
                },
            )

        stored = load_scheduler(self.scheduler)["lanes"][str(lane["laneId"])]
        self.assertEqual(
            stored["conflictDependencies"],
            {conflict: [primary_one, primary_two]},
        )
        self.assertNotIn(replacement_conflict, stored["conflictDependencies"])


if __name__ == "__main__":
    unittest.main()
