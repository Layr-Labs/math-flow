from __future__ import annotations

import unittest

from math_flow.context import _scope_nodes
from math_flow.errors import MathFlowError
from math_flow.viewer import (
    TWO_ENTITY_SEMANTIC_PROFILE,
    _research_v7_viewer_nodes,
)


TX_ONE = "1" * 40
TX_TWO = "2" * 40
JUDGMENT = "sha256:" + "3" * 64


def _program(
    program_id: str,
    *,
    parent_id: str | None,
    title: str,
    sources: list[str],
) -> dict[str, object]:
    return {
        "id": program_id,
        "parentId": parent_id,
        "title": title,
        "objective": f"Objective for {title}.",
        "currentStateSummary": f"Current state of {title}.",
        "localResidualSummary": f"Residual work in {title}.",
        "status": "active",
        "intermediateResultIds": [],
        "sourceTransactionIds": sources,
        "lineage": [],
        "digest": "sha256:" + ("a" if program_id == "root" else "b") * 64,
    }


def _result(
    result_id: str,
    *,
    primary_program_id: str,
    related_program_ids: list[str],
    dependencies: list[str],
    source: str,
) -> dict[str, object]:
    return {
        "id": result_id,
        "primaryProgramId": primary_program_id,
        "relatedProgramIds": related_program_ids,
        "title": f"Result {result_id}",
        "statement": f"Statement for {result_id}.",
        "scopeQualifications": ["Under the fixture hypotheses."],
        "support": {
            "proofs": ["A complete proof."],
            "methods": ["A reusable method."],
            "computations": ["A checked computation."],
            "tools": ["A deterministic audit tool."],
            "artifactRefs": [
                {"path": "artifacts/check.json", "digest": "sha256:" + "4" * 64}
            ],
            "attestationRefs": ["sha256:" + "5" * 64],
        },
        "dependencyResultIds": dependencies,
        "claimRefs": [{"transactionId": source, "claimKey": "claim/main"}],
        "sourceTransactionIds": [source],
        "judgmentIds": [JUDGMENT],
        "status": "active",
        "supersededByResultIds": [],
        "digest": "sha256:" + ("c" if result_id == "main" else "d") * 64,
    }


def _state() -> dict[str, object]:
    state = {
        "schemaVersion": 3,
        "problemId": "demo",
        "programs": {
            "root": _program("root", parent_id=None, title="Root", sources=[]),
            "program/a": _program(
                "program/a", parent_id="root", title="Program A", sources=[TX_ONE]
            ),
            "program/b": _program(
                "program/b", parent_id="root", title="Program B", sources=[TX_TWO]
            ),
        },
        "intermediateResults": {
            "basis": _result(
                "basis",
                primary_program_id="program/b",
                related_program_ids=[],
                dependencies=[],
                source=TX_TWO,
            ),
            "main": _result(
                "main",
                primary_program_id="program/a",
                related_program_ids=["program/b"],
                dependencies=["basis"],
                source=TX_ONE,
            ),
            "unrelated": _result(
                "unrelated",
                primary_program_id="root",
                related_program_ids=[],
                dependencies=[],
                source=TX_TWO,
            ),
        },
        "contributions": {
            TX_ONE: {
                "id": TX_ONE,
                "transactionId": TX_ONE,
                "claimKeys": ["claim/main"],
                "directProgramIds": ["program/a"],
                "intermediateResultIds": ["main"],
                "dependencyTransactionIds": [],
                "judgmentId": JUDGMENT,
                "digest": "sha256:" + "e" * 64,
            }
        },
        "stateDigest": "sha256:" + "f" * 64,
    }
    state["programs"]["program/a"]["intermediateResultIds"] = ["main"]
    state["programs"]["program/b"]["intermediateResultIds"] = ["basis", "main"]
    state["programs"]["root"]["intermediateResultIds"] = ["unrelated"]
    return state


class TwoEntityViewerTests(unittest.TestCase):
    def test_normalizes_exactly_programs_and_intermediate_results(self) -> None:
        nodes = _research_v7_viewer_nodes(
            _state(), {TX_ONE: 1, TX_TWO: 2}
        )

        self.assertEqual(
            {node["type"] for node in nodes.values()},
            {"program", "intermediate-result"},
        )
        self.assertNotIn(TX_ONE, nodes, "contributions must not become knowledge nodes")
        self.assertEqual(nodes["result:main"]["parentId"], "program/a")
        self.assertEqual(nodes["result:main"]["subjects"][0]["ledgerPosition"], 1)
        self.assertIn("## Current state", nodes["program/a"]["contentMarkdown"])
        self.assertIn("## Local residual work", nodes["program/a"]["contentMarkdown"])
        self.assertIn("Result main", nodes["program/a"]["contentMarkdown"])
        self.assertIn("## Proofs", nodes["result:main"]["contentMarkdown"])
        self.assertIn("## Methods", nodes["result:main"]["contentMarkdown"])
        self.assertIn("## Computations", nodes["result:main"]["contentMarkdown"])
        self.assertIn("## Tools", nodes["result:main"]["contentMarkdown"])
        self.assertIn("artifacts/check.json", nodes["result:main"]["contentMarkdown"])
        self.assertIn("## Objective attestations", nodes["result:main"]["contentMarkdown"])
        self.assertIn(
            {
                "kind": "knowledge-node",
                "id": "result:basis",
                "relation": "depends-on",
            },
            nodes["result:main"]["evidence"],
        )
        self.assertIn(
            {
                "kind": "knowledge-node",
                "id": "program/b",
                "relation": "related-program",
            },
            nodes["result:main"]["evidence"],
        )

    def test_scoped_result_context_includes_dependency_and_program_paths(self) -> None:
        nodes = _research_v7_viewer_nodes(_state(), {TX_ONE: 1, TX_TWO: 2})
        normalized_state = {
            "nodes": nodes,
            "stateDigest": "sha256:" + "f" * 64,
            "semanticProfile": TWO_ENTITY_SEMANTIC_PROFILE,
        }

        requested, scoped = _scope_nodes(normalized_state, ["result:main"])

        self.assertEqual(requested, ["result:main"])
        scoped_ids = {node["id"] for node in scoped}
        self.assertTrue(
            {"root", "program/a", "program/b", "result:main", "result:basis"}
            <= scoped_ids
        )
        self.assertNotIn("result:unrelated", scoped_ids)

    def test_rejects_a_state_without_the_two_entity_maps(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "program and intermediate-result"):
            _research_v7_viewer_nodes({"programs": {}}, {})


if __name__ == "__main__":
    unittest.main()
