from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.cli import main
from math_flow.directions import (
    potential_direction_overlaps,
    research_direction_ledger,
    validate_direction_ledger,
)
from math_flow.errors import MathFlowError
from math_flow.repository import ledger, validate_pr, validate_tree


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class ResearchDirectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Direction Author")
        git(self.root, "config", "user.email", "direction@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n\nFind a proof.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Create problem")
        self.initial = git(self.root, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def event(
        self,
        direction_id: str,
        event_id: str,
        value: dict[str, object],
        markdown: str = "# Research plan\n\nDetailed participant-authored plan.\n",
    ) -> str:
        prefix = (
            self.root
            / f"problems/demo/directions/{direction_id}/events/{event_id}"
        )
        write(prefix / "event.json", json.dumps(value, indent=2) + "\n")
        write(prefix / "README.md", markdown)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", f"{value['eventType']} {direction_id}")
        return git(self.root, "rev-parse", "HEAD")

    def registration(
        self, direction_id: str = "modular-construction", event_id: str = "initial-plan"
    ) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "eventType": "register",
            "eventId": event_id,
            "directionId": direction_id,
            "title": "Modular construction",
            "summary": "Search for a modular construction with a verifiable certificate.",
            "relatedKnowledgeNodeIds": ["program/modular-search"],
        }

    def contribution(self, name: str = "certificate") -> str:
        write(
            self.root / f"problems/demo/contributions/{name}/README.md",
            "# Certificate\n\nA checked construction.\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", f"Add {name}")
        return git(self.root, "rev-parse", "HEAD")

    def test_register_update_complete_and_keep_math_ledger_separate(self) -> None:
        before = ledger(self.root, "demo", self.initial)
        registered = self.event(
            "modular-construction", "initial-plan", self.registration()
        )
        validation = validate_pr(self.root, self.initial, registered)
        self.assertEqual(validation["transactionKind"], "direction-event")
        self.assertEqual(validation["eventType"], "register")

        after_registration = ledger(self.root, "demo", registered)
        self.assertEqual(after_registration["transactions"], [])
        self.assertEqual(
            after_registration["problemLedgerDigest"], before["problemLedgerDigest"]
        )

        registration_ledger = research_direction_ledger(
            self.root, "demo", registered
        )
        self.assertEqual(validate_direction_ledger(registration_ledger), registration_ledger)
        self.assertEqual(registration_ledger["directionLedgerHead"], registered)
        self.assertEqual(registration_ledger["events"][0]["canonicalOrdinal"], 2)
        self.assertEqual(
            registration_ledger["directions"][0]["status"], "active"
        )

        updated = self.event(
            "modular-construction",
            "narrow-search",
            {
                "schemaVersion": 1,
                "eventType": "update",
                "eventId": "narrow-search",
                "directionId": "modular-construction",
                "previousEventId": "initial-plan",
                "title": "Narrow modular construction",
                "summary": "Restrict the search to two explicitly defined residue families.",
                "relatedKnowledgeNodeIds": ["program/modular-search"],
            },
        )
        self.assertEqual(
            validate_pr(self.root, registered, updated)["eventType"], "update"
        )
        contribution = self.contribution()
        completed = self.event(
            "modular-construction",
            "certificate-complete",
            {
                "schemaVersion": 1,
                "eventType": "complete",
                "eventId": "certificate-complete",
                "directionId": "modular-construction",
                "previousEventId": "narrow-search",
                "summary": "The submitted certificate completes the registered search.",
                "contributionTransactionIds": [contribution],
            },
        )
        completion = validate_pr(self.root, contribution, completed)
        self.assertEqual(completion["eventType"], "complete")
        state = research_direction_ledger(self.root, "demo", completed)
        direction = state["directions"][0]
        self.assertEqual(direction["status"], "completed")
        self.assertEqual(direction["title"], "Narrow modular construction")
        self.assertEqual(direction["completionTransactionIds"], [contribution])
        self.assertEqual(
            validate_tree(self.root),
            {
                "problems": 1,
                "contributions": 1,
                "researchDirections": 1,
                "directionEvents": 3,
            },
        )

    def test_rejects_stale_predecessor_and_changes_after_release(self) -> None:
        registered = self.event(
            "modular-construction", "initial-plan", self.registration()
        )
        stale = self.event(
            "modular-construction",
            "bad-update",
            {
                "schemaVersion": 1,
                "eventType": "update",
                "eventId": "bad-update",
                "directionId": "modular-construction",
                "previousEventId": "missing",
                "title": "Bad update",
                "summary": "This update does not extend the current event.",
                "relatedKnowledgeNodeIds": [],
            },
        )
        with self.assertRaisesRegex(MathFlowError, "current terminal"):
            validate_pr(self.root, registered, stale)

        git(self.root, "reset", "--hard", registered)
        released = self.event(
            "modular-construction",
            "released",
            {
                "schemaVersion": 1,
                "eventType": "release",
                "eventId": "released",
                "directionId": "modular-construction",
                "previousEventId": "initial-plan",
                "reason": "The approach is no longer being actively pursued.",
            },
        )
        later = self.event(
            "modular-construction",
            "late-update",
            {
                "schemaVersion": 1,
                "eventType": "update",
                "eventId": "late-update",
                "directionId": "modular-construction",
                "previousEventId": "released",
                "title": "Late update",
                "summary": "This cannot reopen a released direction.",
                "relatedKnowledgeNodeIds": [],
            },
        )
        with self.assertRaisesRegex(MathFlowError, "already released"):
            validate_pr(self.root, released, later)
        with self.assertRaisesRegex(MathFlowError, "changes after it is released"):
            research_direction_ledger(self.root, "demo", later)

    def test_only_originating_author_may_release_direction(self) -> None:
        registered = self.event(
            "modular-construction", "initial-plan", self.registration()
        )
        git(self.root, "config", "user.name", "Other Agent")
        git(self.root, "config", "user.email", "other-agent@example.com")
        released = self.event(
            "modular-construction",
            "unauthorized-release",
            {
                "schemaVersion": 1,
                "eventType": "release",
                "eventId": "unauthorized-release",
                "directionId": "modular-construction",
                "previousEventId": "initial-plan",
                "reason": "Another agent must not release this registration.",
            },
        )
        with self.assertRaisesRegex(MathFlowError, "originating register event author"):
            validate_pr(self.root, registered, released)
        with self.assertRaisesRegex(MathFlowError, "originating register event author"):
            research_direction_ledger(self.root, "demo", released)

        git(self.root, "reset", "--hard", registered)
        git(self.root, "config", "user.name", "Direction Author")
        git(self.root, "config", "user.email", "direction@example.com")
        authorized_release = self.event(
            "modular-construction",
            "authorized-release",
            {
                "schemaVersion": 1,
                "eventType": "release",
                "eventId": "authorized-release",
                "directionId": "modular-construction",
                "previousEventId": "initial-plan",
                "reason": "The originating agent is no longer pursuing this direction.",
            },
        )
        self.assertEqual(
            validate_pr(self.root, registered, authorized_release)["eventType"],
            "release",
        )
        self.assertEqual(
            research_direction_ledger(self.root, "demo", authorized_release)[
                "directions"
            ][0]["status"],
            "released",
        )

    def test_tree_rejects_noncanonical_event_files(self) -> None:
        prefix = self.root / "problems/demo/directions/test/events/initial"
        write(prefix / "README.md", "# Plan\n")
        write(prefix / "event.json", json.dumps(self.registration("test", "initial")))
        write(prefix / "notes.txt", "unexpected")
        with self.assertRaisesRegex(MathFlowError, "exactly README.md and event.json"):
            validate_tree(self.root)

    def test_pr_rejects_direction_event_symlinks(self) -> None:
        prefix = self.root / "problems/demo/directions/test/events/initial"
        prefix.mkdir(parents=True)
        (prefix / "README.md").symlink_to("event.json")
        write(prefix / "event.json", json.dumps(self.registration("test", "initial")))
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add unsafe direction event")
        with self.assertRaisesRegex(MathFlowError, "may not be symlinks"):
            validate_pr(self.root, self.initial, "HEAD")

    def test_reports_only_mechanical_active_overlap(self) -> None:
        directions = [
            {
                "directionId": "a",
                "status": "active",
                "relatedKnowledgeNodeIds": ["program/a", "shared"],
            },
            {
                "directionId": "b",
                "status": "active",
                "relatedKnowledgeNodeIds": ["shared"],
            },
            {
                "directionId": "c",
                "status": "released",
                "relatedKnowledgeNodeIds": ["shared"],
            },
        ]
        self.assertEqual(
            potential_direction_overlaps(directions),
            [
                {
                    "directionIds": ["a", "b"],
                    "sharedKnowledgeNodeIds": ["shared"],
                }
            ],
        )

    def test_embedded_ledger_rejects_tampered_event_markdown(self) -> None:
        registered = self.event(
            "modular-construction", "initial-plan", self.registration()
        )
        state = research_direction_ledger(self.root, "demo", registered)
        state["events"][0]["contentMarkdown"] = "Changed after hashing."
        with self.assertRaisesRegex(MathFlowError, "content digest"):
            validate_direction_ledger(state)

    def test_directions_cli_writes_filtered_canonical_state(self) -> None:
        registered = self.event(
            "modular-construction", "initial-plan", self.registration()
        )
        output = self.root / "active-directions.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "directions",
                    "--problem",
                    "demo",
                    "--head",
                    registered,
                    "--status",
                    "active",
                    "--output",
                    str(output),
                ]
            ),
            0,
        )
        value = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(value["ledgerHead"], registered)
        self.assertEqual(
            [item["directionId"] for item in value["directions"]],
            ["modular-construction"],
        )


if __name__ == "__main__":
    unittest.main()
