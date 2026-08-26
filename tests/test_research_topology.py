from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.research_state import (
    empty_research_program_state,
    validate_research_program_state,
)
from math_flow.research_topology import (
    _with_record_digest,
    _with_state_digest,
    apply_research_topology_transition,
    derive_research_topology_alignment,
    empty_research_program_state_v2,
    validate_research_program_state_v2,
    validate_research_program_state_versioned,
    validate_research_topology_alignment,
)


TRANSACTION = "a" * 40
JUDGMENT = "sha256:" + "b" * 64


def _program(
    program_id: str,
    parent_id: str | None,
    parent_thread_ids: list[str],
    *,
    status: str = "active",
    lineage: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    return _with_record_digest(
        {
            "id": program_id,
            "parentId": parent_id,
            "title": program_id.replace("program/", "").title(),
            "objective": f"Advance {program_id}.",
            "status": status,
            "parentThreadIds": parent_thread_ids,
            "sourceTransactionIds": [] if program_id == "root" else [TRANSACTION],
            "lineage": lineage or [],
        }
    )


def _thread(
    thread_id: str,
    program_id: str,
    *,
    kind: str = "research",
    status: str = "active",
    exposure: str = "1",
) -> dict[str, object]:
    return _with_record_digest(
        {
            "id": thread_id,
            "programId": program_id,
            "title": thread_id.replace("/", " ").title(),
            "summary": f"Research thread {thread_id}.",
            "kind": kind,
            "status": status,
            "expectedExposure": exposure,
            "conditions": [],
            "sourceTransactionIds": (
                [] if thread_id == "root/unstructured-search" else [TRANSACTION]
            ),
        }
    )


def _item(item_id: str, program_id: str) -> dict[str, object]:
    return _with_record_digest(
        {
            "id": item_id,
            "programId": program_id,
            "type": "result",
            "title": "Accepted result",
            "summary": "An accepted result.",
            "claimRefs": [
                {"transactionId": TRANSACTION, "claimKey": "claim/main"}
            ],
            "sourceTransactionIds": [TRANSACTION],
            "dependencyItemIds": [],
        }
    )


def _contribution() -> dict[str, object]:
    return _with_record_digest(
        {
            "id": TRANSACTION,
            "transactionId": TRANSACTION,
            "claimKeys": ["claim/main"],
            "directProgramId": "program/a",
            "directThreadIds": ["program/a/work"],
            "itemIds": ["result/a"],
            "dependencyTransactionIds": [],
            "judgmentId": JUDGMENT,
        }
    )


def _base_state() -> dict[str, object]:
    state = {
        "schemaVersion": 2,
        "problemId": "demo",
        "ledgerHead": TRANSACTION,
        "baseStateDigest": None,
        "rootProgramId": "root",
        "programs": {
            "root": _program("root", None, []),
            "program/a": _program("program/a", "root", ["root/a-entry"]),
            "program/b": _program("program/b", "root", ["root/b-entry"]),
        },
        "threads": {
            "root/unstructured-search": _thread(
                "root/unstructured-search", "root", kind="unstructured"
            ),
            "root/a-entry": _thread("root/a-entry", "root"),
            "root/b-entry": _thread("root/b-entry", "root"),
            "program/a/unstructured": _thread(
                "program/a/unstructured", "program/a", kind="unstructured"
            ),
            "program/a/work": _thread("program/a/work", "program/a"),
            "program/b/unstructured": _thread(
                "program/b/unstructured", "program/b", kind="unstructured"
            ),
        },
        "items": {"result/a": _item("result/a", "program/a")},
        "contributions": {TRANSACTION: _contribution()},
    }
    result = _with_state_digest(state)
    validate_research_program_state_v2(result)
    return result


def _value(record: dict[str, object], **updates: object) -> dict[str, object]:
    value = {key: copy.deepcopy(item) for key, item in record.items() if key != "digest"}
    value.update(updates)
    return value


def _operation(
    action: str,
    kind: str,
    entity_id: str,
    value: dict[str, object],
    *,
    base: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "action": action,
        "entityKind": kind,
        "entityId": entity_id,
        "baseDigest": None if base is None else base["digest"],
        "value": value,
    }


def _transition(
    state: dict[str, object], operations: list[dict[str, object]]
) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "baseStateDigest": state["stateDigest"],
        "operations": operations,
    }


def _split_operations(state: dict[str, object]) -> list[dict[str, object]]:
    programs = state["programs"]
    threads = state["threads"]
    items = state["items"]
    assert isinstance(programs, dict)
    assert isinstance(threads, dict)
    assert isinstance(items, dict)
    left = _program(
        "program/left",
        "root",
        ["root/a-entry"],
        lineage=[{"relation": "split-from", "programId": "program/a"}],
    )
    right_entry = _thread("root/right-entry", "root")
    right = _program(
        "program/right",
        "root",
        ["root/right-entry"],
        lineage=[{"relation": "split-from", "programId": "program/a"}],
    )
    right_unstructured = _thread(
        "program/right/unstructured", "program/right", kind="unstructured"
    )
    predecessor_lineage = [
        {"relation": "split-into", "programId": "program/left"},
        {"relation": "split-into", "programId": "program/right"},
    ]
    return [
        _operation(
            "create",
            "thread",
            "root/right-entry",
            _value(right_entry),
            base=None,
        ),
        _operation(
            "create", "program", "program/left", _value(left), base=None
        ),
        _operation(
            "create", "program", "program/right", _value(right), base=None
        ),
        _operation(
            "create",
            "thread",
            "program/right/unstructured",
            _value(right_unstructured),
            base=None,
        ),
        _operation(
            "move",
            "thread",
            "program/a/unstructured",
            _value(threads["program/a/unstructured"], programId="program/left"),
            base=threads["program/a/unstructured"],
        ),
        _operation(
            "move",
            "thread",
            "program/a/work",
            _value(threads["program/a/work"], programId="program/left"),
            base=threads["program/a/work"],
        ),
        _operation(
            "move",
            "item",
            "result/a",
            _value(items["result/a"], programId="program/left"),
            base=items["result/a"],
        ),
        _operation(
            "retire",
            "program",
            "program/a",
            _value(programs["program/a"], status="retired", lineage=predecessor_lineage),
            base=programs["program/a"],
        ),
    ]


def _merge_operations(state: dict[str, object]) -> list[dict[str, object]]:
    programs = state["programs"]
    threads = state["threads"]
    items = state["items"]
    assert isinstance(programs, dict)
    assert isinstance(threads, dict)
    assert isinstance(items, dict)
    successor = _program(
        "program/merged",
        "root",
        ["root/a-entry"],
        lineage=[
            {"relation": "merged-from", "programId": "program/a"},
            {"relation": "merged-from", "programId": "program/b"},
        ],
    )
    return [
        _operation(
            "create", "program", "program/merged", _value(successor), base=None
        ),
        _operation(
            "move",
            "thread",
            "program/a/unstructured",
            _value(
                threads["program/a/unstructured"], programId="program/merged"
            ),
            base=threads["program/a/unstructured"],
        ),
        _operation(
            "move",
            "thread",
            "program/a/work",
            _value(threads["program/a/work"], programId="program/merged"),
            base=threads["program/a/work"],
        ),
        _operation(
            "retire",
            "thread",
            "program/b/unstructured",
            _value(
                threads["program/b/unstructured"],
                status="retired",
                expectedExposure="0",
            ),
            base=threads["program/b/unstructured"],
        ),
        _operation(
            "move",
            "item",
            "result/a",
            _value(items["result/a"], programId="program/merged"),
            base=items["result/a"],
        ),
        _operation(
            "retire",
            "program",
            "program/a",
            _value(
                programs["program/a"],
                status="retired",
                lineage=[
                    {"relation": "merged-into", "programId": "program/merged"}
                ],
            ),
            base=programs["program/a"],
        ),
        _operation(
            "retire",
            "program",
            "program/b",
            _value(
                programs["program/b"],
                status="retired",
                lineage=[
                    {"relation": "merged-into", "programId": "program/merged"}
                ],
            ),
            base=programs["program/b"],
        ),
    ]


class ResearchTopologyTests(unittest.TestCase):
    def test_empty_v2_state_and_legacy_v1_remain_distinct_and_valid(self) -> None:
        evolved = empty_research_program_state_v2("demo")
        validate_research_program_state_v2(evolved)
        legacy = empty_research_program_state("demo")
        validate_research_program_state(legacy)
        self.assertIs(validate_research_program_state_versioned(legacy), legacy)
        self.assertIs(validate_research_program_state_versioned(evolved), evolved)
        with self.assertRaisesRegex(MathFlowError, "unsupported version"):
            validate_research_program_state_v2(legacy)

    def test_move_preserves_identity_and_derives_canonical_alignment(self) -> None:
        state = _base_state()
        programs = state["programs"]
        assert isinstance(programs, dict)
        parent_thread = _thread("program/b/a-entry", "program/b")
        operations = [
            _operation(
                "create",
                "thread",
                "program/b/a-entry",
                _value(parent_thread),
                base=None,
            ),
            _operation(
                "move",
                "program",
                "program/a",
                _value(
                    programs["program/a"],
                    parentId="program/b",
                    parentThreadIds=["program/b/a-entry"],
                ),
                base=programs["program/a"],
            ),
        ]
        post_state, alignment = apply_research_topology_transition(
            state, _transition(state, operations)
        )
        moved = next(
            item for item in alignment["moved"] if item["entityId"] == "program/a"
        )
        self.assertEqual(moved["fromParentId"], "root")
        self.assertEqual(moved["toParentId"], "program/b")
        self.assertEqual(post_state["programs"]["program/a"]["title"], "A")
        self.assertEqual(alignment, derive_research_topology_alignment(state, post_state))
        validate_research_topology_alignment(alignment, state, post_state)

    def test_move_cannot_rewrite_content(self) -> None:
        state = _base_state()
        program = state["programs"]["program/a"]
        operation = _operation(
            "move",
            "program",
            "program/a",
            _value(program, title="Rewritten"),
            base=program,
        )
        with self.assertRaisesRegex(MathFlowError, "preserve identity, content"):
            apply_research_topology_transition(state, _transition(state, [operation]))

    def test_hierarchy_cycle_is_rejected(self) -> None:
        state = _base_state()
        program = state["programs"]["program/a"]
        operation = _operation(
            "move",
            "program",
            "program/a",
            _value(
                program,
                parentId="program/a",
                parentThreadIds=["program/a/work"],
            ),
            base=program,
        )
        with self.assertRaisesRegex(MathFlowError, "hierarchy contains a cycle"):
            apply_research_topology_transition(state, _transition(state, [operation]))

    def test_stale_state_and_entity_guards_are_rejected(self) -> None:
        state = _base_state()
        program = state["programs"]["program/a"]
        operation = _operation(
            "move",
            "program",
            "program/a",
            _value(program, lineage=[{"relation": "split-from", "programId": "program/b"}]),
            base=program,
        )
        stale_state = _transition(state, [operation])
        stale_state["baseStateDigest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(MathFlowError, "stale base state"):
            apply_research_topology_transition(state, stale_state)
        stale_entity = _transition(state, [copy.deepcopy(operation)])
        stale_entity["operations"][0]["baseDigest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(
            MathFlowError,
            "baseDigest mismatch: move program program/a expected "
            + str(program["digest"]),
        ):
            apply_research_topology_transition(state, stale_entity)

        duplicate_create = _operation(
            "create",
            "program",
            "program/a",
            _value(program),
            base=None,
        )
        with self.assertRaisesRegex(
            MathFlowError,
            "create requires a new ID, but the entity already exists: program program/a",
        ):
            apply_research_topology_transition(
                state, _transition(state, [duplicate_create])
            )

    def test_atomic_split_is_complete_and_alignment_is_deterministic(self) -> None:
        state = _base_state()
        operations = _split_operations(state)
        post_state, alignment = apply_research_topology_transition(
            state, _transition(state, operations)
        )
        reverse_post_state, reverse_alignment = apply_research_topology_transition(
            state, _transition(state, list(reversed(operations)))
        )
        reordered_lineage = copy.deepcopy(operations)
        predecessor = next(
            operation
            for operation in reordered_lineage
            if operation["entityId"] == "program/a"
        )
        predecessor["value"]["lineage"].reverse()
        reordered_post_state, reordered_alignment = apply_research_topology_transition(
            state, _transition(state, reordered_lineage)
        )
        self.assertEqual(
            alignment["splits"],
            [
                {
                    "predecessorProgramId": "program/a",
                    "successorProgramIds": ["program/left", "program/right"],
                }
            ],
        )
        self.assertIn(
            ("program", "program/a"),
            {(item["entityKind"], item["entityId"]) for item in alignment["retired"]},
        )
        self.assertEqual(post_state["items"]["result/a"]["programId"], "program/left")
        self.assertEqual(
            post_state["contributions"][TRANSACTION]["directProgramId"], "program/a"
        )
        self.assertEqual(
            alignment["alignmentDigest"],
            derive_research_topology_alignment(state, post_state)["alignmentDigest"],
        )
        self.assertEqual(reverse_post_state, post_state)
        self.assertEqual(reverse_alignment, alignment)
        self.assertEqual(reordered_post_state, post_state)
        self.assertEqual(reordered_alignment, alignment)

    def test_partial_split_leaving_item_in_retired_program_is_rejected(self) -> None:
        state = _base_state()
        operations = [
            operation
            for operation in _split_operations(state)
            if not (
                operation["entityKind"] == "item"
                and operation["entityId"] == "result/a"
            )
        ]
        with self.assertRaisesRegex(MathFlowError, "item remains in a retired program"):
            apply_research_topology_transition(state, _transition(state, operations))

    def test_split_successor_can_later_split_without_losing_prior_lineage(self) -> None:
        state = _base_state()
        first_state, _ = apply_research_topology_transition(
            state, _transition(state, _split_operations(state))
        )
        programs = first_state["programs"]
        threads = first_state["threads"]
        items = first_state["items"]
        assert isinstance(programs, dict)
        assert isinstance(threads, dict)
        assert isinstance(items, dict)
        next_entry = _thread("root/left-two-entry", "root")
        left_one = _program(
            "program/left-one",
            "root",
            ["root/a-entry"],
            lineage=[
                {"relation": "split-from", "programId": "program/left"}
            ],
        )
        left_two = _program(
            "program/left-two",
            "root",
            ["root/left-two-entry"],
            lineage=[
                {"relation": "split-from", "programId": "program/left"}
            ],
        )
        left_two_unstructured = _thread(
            "program/left-two/unstructured",
            "program/left-two",
            kind="unstructured",
        )
        predecessor_lineage = [
            {"relation": "split-from", "programId": "program/a"},
            {"relation": "split-into", "programId": "program/left-one"},
            {"relation": "split-into", "programId": "program/left-two"},
        ]
        operations = [
            _operation(
                "create",
                "thread",
                "root/left-two-entry",
                _value(next_entry),
                base=None,
            ),
            _operation(
                "create",
                "program",
                "program/left-one",
                _value(left_one),
                base=None,
            ),
            _operation(
                "create",
                "program",
                "program/left-two",
                _value(left_two),
                base=None,
            ),
            _operation(
                "create",
                "thread",
                "program/left-two/unstructured",
                _value(left_two_unstructured),
                base=None,
            ),
            _operation(
                "move",
                "thread",
                "program/a/unstructured",
                _value(
                    threads["program/a/unstructured"],
                    programId="program/left-one",
                ),
                base=threads["program/a/unstructured"],
            ),
            _operation(
                "move",
                "thread",
                "program/a/work",
                _value(threads["program/a/work"], programId="program/left-one"),
                base=threads["program/a/work"],
            ),
            _operation(
                "move",
                "item",
                "result/a",
                _value(items["result/a"], programId="program/left-one"),
                base=items["result/a"],
            ),
            _operation(
                "retire",
                "program",
                "program/left",
                _value(
                    programs["program/left"],
                    status="retired",
                    lineage=predecessor_lineage,
                ),
                base=programs["program/left"],
            ),
        ]
        post_state, alignment = apply_research_topology_transition(
            first_state, _transition(first_state, operations)
        )
        self.assertEqual(
            post_state["programs"]["program/left"]["lineage"][0],
            {"relation": "split-from", "programId": "program/a"},
        )
        self.assertEqual(
            alignment["splits"],
            [
                {
                    "predecessorProgramId": "program/left",
                    "successorProgramIds": [
                        "program/left-one",
                        "program/left-two",
                    ],
                }
            ],
        )

    def test_active_child_beneath_retired_program_is_rejected(self) -> None:
        state = _base_state()
        programs = state["programs"]
        assert isinstance(programs, dict)
        child = _program("program/child", "program/a", ["program/a/work"])
        child_unstructured = _thread(
            "program/child/unstructured", "program/child", kind="unstructured"
        )
        operations = [
            _operation("create", "program", "program/child", _value(child), base=None),
            _operation(
                "create",
                "thread",
                "program/child/unstructured",
                _value(child_unstructured),
                base=None,
            ),
            _operation(
                "retire",
                "program",
                "program/a",
                _value(programs["program/a"], status="retired"),
                base=programs["program/a"],
            ),
        ]
        with self.assertRaisesRegex(MathFlowError, "retired ancestor"):
            apply_research_topology_transition(state, _transition(state, operations))

    def test_nonreciprocal_and_duplicate_split_lineage_are_rejected(self) -> None:
        state = _base_state()
        nonreciprocal = _split_operations(state)
        successor = next(
            operation
            for operation in nonreciprocal
            if operation["entityId"] == "program/right"
        )
        successor["value"]["lineage"] = []
        with self.assertRaisesRegex(MathFlowError, "lineage is not reciprocal"):
            apply_research_topology_transition(
                state, _transition(state, nonreciprocal)
            )

        duplicate = _split_operations(state)
        predecessor = next(
            operation
            for operation in duplicate
            if operation["entityId"] == "program/a"
        )
        predecessor["value"]["lineage"].append(
            {"relation": "split-into", "programId": "program/right"}
        )
        with self.assertRaisesRegex(MathFlowError, "duplicate research program lineage"):
            apply_research_topology_transition(state, _transition(state, duplicate))

    def test_single_successor_split_is_rejected_as_incomplete(self) -> None:
        state = _base_state()
        operations = _split_operations(state)
        predecessor = next(
            operation
            for operation in operations
            if operation["entityId"] == "program/a"
        )
        predecessor["value"]["lineage"] = predecessor["value"]["lineage"][:1]
        with self.assertRaisesRegex(MathFlowError, "at least two successors"):
            apply_research_topology_transition(state, _transition(state, operations))

    def test_atomic_merge_retires_predecessors_and_deduplicates_unstructured_thread(self) -> None:
        state = _base_state()
        post_state, alignment = apply_research_topology_transition(
            state, _transition(state, _merge_operations(state))
        )
        self.assertEqual(
            alignment["merges"],
            [
                {
                    "predecessorProgramIds": ["program/a", "program/b"],
                    "successorProgramId": "program/merged",
                }
            ],
        )
        self.assertEqual(
            post_state["threads"]["program/b/unstructured"]["status"], "retired"
        )
        retired = {
            (item["entityKind"], item["entityId"]) for item in alignment["retired"]
        }
        self.assertIn(("thread", "program/b/unstructured"), retired)

    def test_partial_and_nonreciprocal_merges_are_rejected(self) -> None:
        state = _base_state()
        partial = _merge_operations(state)
        successor = next(
            operation
            for operation in partial
            if operation["entityId"] == "program/merged"
        )
        successor["value"]["lineage"] = successor["value"]["lineage"][:1]
        omitted_predecessor = next(
            operation
            for operation in partial
            if operation["entityId"] == "program/b"
        )
        omitted_predecessor["value"]["lineage"] = []
        with self.assertRaisesRegex(MathFlowError, "at least two predecessors"):
            apply_research_topology_transition(state, _transition(state, partial))

        nonreciprocal = _merge_operations(state)
        predecessor = next(
            operation
            for operation in nonreciprocal
            if operation["entityId"] == "program/b"
        )
        predecessor["value"]["lineage"] = []
        with self.assertRaisesRegex(MathFlowError, "lineage is not reciprocal"):
            apply_research_topology_transition(
                state, _transition(state, nonreciprocal)
            )

    def test_alignment_tampering_is_rejected(self) -> None:
        state = _base_state()
        post_state, alignment = apply_research_topology_transition(
            state, _transition(state, _split_operations(state))
        )
        tampered = copy.deepcopy(alignment)
        tampered["splits"][0]["successorProgramIds"].reverse()
        with self.assertRaisesRegex(MathFlowError, "differs from the deterministic"):
            validate_research_topology_alignment(tampered, state, post_state)

    def test_versioned_schema_contracts_are_additive(self) -> None:
        root = Path(__file__).parents[1]
        for name in (
            "research-program-state-v2.schema.json",
            "research-program-topology-transition-v1.schema.json",
            "research-program-topology-alignment-v1.schema.json",
        ):
            schema = json.loads((root / "protocol" / "schemas" / name).read_text())
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        legacy = json.loads(
            (root / "protocol" / "schemas" / "research-program-state.schema.json").read_text()
        )
        self.assertEqual(legacy["properties"]["schemaVersion"], {"const": 1})
        self.assertNotIn("lineage", legacy["$defs"]["program"]["properties"])


if __name__ == "__main__":
    unittest.main()
