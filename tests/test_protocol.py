from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.judges import project, render_request
from math_flow.knowledge import apply_deltas, apply_revision_deltas, empty_state
from math_flow.openrouter import format_error_message
from math_flow.repository import ledger, validate_pr, validate_tree
from math_flow.runs import run_judge_bundle


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, text=True
    )
    return result.stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class RepositoryValidationTests(unittest.TestCase):
    def test_current_tree_is_valid(self) -> None:
        root = Path(__file__).parents[1]
        self.assertEqual(validate_tree(root), {"problems": 1, "contributions": 1})

    def test_empty_readme_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / "problems/p/problem.md", "A problem")
            write(root / "problems/p/contributions/c/README.md", "   \n")
            with self.assertRaisesRegex(MathFlowError, "must exist and contain text"):
                validate_tree(root)

    def test_loose_file_in_contributions_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / "problems/p/problem.md", "A problem")
            write(root / "problems/p/contributions/loose.txt", "not a transaction")
            with self.assertRaisesRegex(MathFlowError, "only contain contribution directories"):
                validate_tree(root)

    def test_openrouter_error_metadata_is_safely_summarized(self) -> None:
        error = {
            "message": "Provider returned error",
            "metadata": {
                "error_type": "invalid_request",
                "provider_name": "OpenAI",
                "provider_code": "invalid_json_schema",
                "raw": "potentially sensitive provider payload",
            },
        }
        rendered = format_error_message(error)
        self.assertIn("provider_code=invalid_json_schema", rendered)
        self.assertNotIn("potentially sensitive", rendered)


class GitProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test Author")
        git(self.root, "config", "user.email", "test@example.com")
        write(self.root / "problems/demo/problem.md", "# Demo\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Create problem")
        self.base = git(self.root, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit_contribution(self, contribution: str, body: str = "# Claim\n\nProof.") -> str:
        write(self.root / f"problems/demo/contributions/{contribution}/README.md", body)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", f"Add {contribution}")
        return git(self.root, "rev-parse", "HEAD")

    def test_valid_atomic_pr_and_ledger(self) -> None:
        head = self.commit_contribution("first-proof")
        result = validate_pr(self.root, self.base, head)
        self.assertEqual(result["contributionId"], "first-proof")
        state = ledger(self.root, "demo", head)
        self.assertEqual(state["ledgerHead"], head)
        self.assertEqual(state["transactions"][0]["transactionId"], head)
        self.assertEqual(state["transactions"][0]["ordinal"], 1)

    def test_pr_cannot_edit_problem_statement(self) -> None:
        self.commit_contribution("first-proof")
        write(self.root / "problems/demo/problem.md", "Changed")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Also change problem")
        head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "may only change"):
            validate_pr(self.root, self.base, head)

    def test_pr_cannot_add_two_contributions(self) -> None:
        write(self.root / "problems/demo/contributions/one/README.md", "One")
        write(self.root / "problems/demo/contributions/two/README.md", "Two")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add two")
        head = git(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "exactly one"):
            validate_pr(self.root, self.base, head)

    def test_projection_is_deterministic(self) -> None:
        head = self.commit_contribution("first-proof", "# Lemma\n\nA useful argument.")
        judge = Path(__file__).parents[1] / "protocol/judges/baseline-v1.json"
        first = project(self.root, "demo", judge, head)
        second = project(self.root, "demo", judge, head)
        self.assertEqual(first, second)
        self.assertEqual(first["contributionVerdicts"][0]["status"], "unassessed")
        self.assertEqual(first["judgeRunner"]["implementation"], "baseline-neutral-v1")
        self.assertEqual(first["projectionDigest"], second["projectionDigest"])

    def test_openrouter_request_and_projection_with_fake_transport(self) -> None:
        head = self.commit_contribution("first-proof", "# Lemma\n\nA useful argument.")
        judge = Path(__file__).parents[1] / "protocol/judges/openrouter-math-review-v1.json"
        request = render_request(self.root, "demo", judge, head)
        self.assertEqual(request["model"], "openai/gpt-5-mini")
        self.assertTrue(request["provider"]["require_parameters"])
        self.assertEqual(request["provider"]["data_collection"], "deny")
        self.assertIn("A useful argument", request["messages"][1]["content"])
        request_schema = request["response_format"]["json_schema"]["schema"]
        self.assertNotIn("uniqueItems", json.dumps(request_schema))

        def fake_transport(payload: dict[str, object]) -> dict[str, object]:
            self.assertEqual(payload, request)
            content = {
                "contributionVerdicts": [
                    {
                        "transactionId": head,
                        "status": "accepted",
                        "confidence": 0.91,
                        "rationale": "The argument is complete for the stated lemma.",
                    }
                ],
                "knowledgeState": {
                    "summary": "The lemma has been established.",
                    "establishedClaims": ["The lemma holds."],
                    "openQuestions": [],
                    "disputes": [],
                },
                "creditAssignments": [
                    {
                        "participant": "Test Author",
                        "transactionIds": [head],
                        "score": 1.0,
                        "rationale": "This is the only accepted contribution.",
                    }
                ],
            }
            return {
                "id": "generation-test",
                "model": "openai/gpt-5-mini",
                "choices": [{"message": {"role": "assistant", "content": json.dumps(content)}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
            }

        result = project(self.root, "demo", judge, head, transport=fake_transport)
        self.assertEqual(result["contributionVerdicts"][0]["status"], "accepted")
        self.assertEqual(result["providerRun"]["responseId"], "generation-test")
        self.assertTrue(result["judgeRequestDigest"].startswith("sha256:"))

    def test_openrouter_projection_rejects_invalid_credit_total(self) -> None:
        head = self.commit_contribution("first-proof")
        judge = Path(__file__).parents[1] / "protocol/judges/openrouter-math-review-v1.json"

        def fake_transport(_: dict[str, object]) -> dict[str, object]:
            content = {
                "contributionVerdicts": [
                    {
                        "transactionId": head,
                        "status": "uncertain",
                        "confidence": 0.5,
                        "rationale": "More checking is needed.",
                    }
                ],
                "knowledgeState": {
                    "summary": "Unresolved.",
                    "establishedClaims": [],
                    "openQuestions": ["Is the proof complete?"],
                    "disputes": [],
                },
                "creditAssignments": [
                    {
                        "participant": "Test Author",
                        "transactionIds": [head],
                        "score": 0.4,
                        "rationale": "Partial progress.",
                    }
                ],
            }
            return {"choices": [{"message": {"content": json.dumps(content)}}]}

        with self.assertRaisesRegex(MathFlowError, "sum to 1.0"):
            project(self.root, "demo", judge, head, transport=fake_transport)

    def test_flat_projection_can_be_written_as_generic_bundle(self) -> None:
        head = self.commit_contribution("first-proof")
        judge = Path(__file__).parents[1] / "protocol/judges/baseline-v1.json"
        output = self.root / "generated-flat-run"
        manifest = run_judge_bundle(self.root, "demo", judge, head, output)
        self.assertEqual(manifest["outputProfile"], "math-flow/flat-json-v1")
        self.assertEqual(manifest["ledgerHead"], head)
        self.assertEqual(manifest["artifacts"][0]["role"], "flat-projection")
        self.assertTrue((output / "run.json").is_file())
        self.assertTrue((output / "projection.json").is_file())

    def test_hierarchical_markdown_run_selects_and_updates_state(self) -> None:
        head = self.commit_contribution("first-proof")
        judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-hierarchical-markdown-v1.json"
        )
        output = self.root / "generated-hierarchical-run"
        requests: list[dict[str, object]] = []

        def response(content: object, index: int) -> dict[str, object]:
            rendered = content if isinstance(content, str) else json.dumps(content)
            return {
                "id": f"generation-{index}",
                "model": "openai/gpt-5-mini",
                "choices": [{"message": {"content": rendered}}],
                "usage": {"total_tokens": 100 + index},
            }

        staged_responses = iter(
            [
                response(
                    {
                        "selectedNodeIds": ["root"],
                        "rationale": "The first contribution may establish a new research program.",
                    },
                    1,
                ),
                response(
                    "# Research assessment\n\n"
                    "The contribution gives a complete proof and motivates an affine program.\n\n"
                    "## Node: program/affine\n\n"
                    "This program studies the problem through affine invariance and area scaling.\n",
                    2,
                ),
                response(
                    {
                        "operations": [
                            {
                                "action": "upsert",
                                "nodeId": "program/affine",
                                "parentId": "root",
                                "nodeType": "program",
                                "title": "Affine methods",
                                "summary": "Use affine invariance and area scaling.",
                                "reportSection": "## Node: program/affine",
                                "baseDigest": None,
                                "transactionIds": [head],
                            }
                        ]
                    },
                    3,
                ),
            ]
        )

        def fake_transport(payload: dict[str, object]) -> dict[str, object]:
            requests.append(payload)
            return next(staged_responses)

        manifest = run_judge_bundle(
            self.root, "demo", judge, head, output, transport=fake_transport
        )
        self.assertEqual(len(requests), 3)
        self.assertIn("response_format", requests[0])
        self.assertNotIn("response_format", requests[1])
        self.assertIn("response_format", requests[2])
        self.assertNotIn("uniqueItems", json.dumps(requests))
        self.assertIn("Do not output JSON", requests[1]["messages"][1]["content"])
        self.assertEqual(manifest["outputProfile"], "math-flow/hierarchical-markdown-v1")
        self.assertEqual(len(manifest["requestDigests"]), 3)
        report = (output / "report.md").read_text(encoding="utf-8")
        self.assertIn("## Node: program/affine", report)
        state = json.loads((output / "state/state.json").read_text(encoding="utf-8"))
        node = state["nodes"]["program/affine"]
        self.assertEqual(node["parentId"], "root")
        self.assertEqual(node["reportRef"]["digest"], next(
            item["digest"] for item in manifest["artifacts"] if item["role"] == "report"
        ))
        self.assertIn("affine invariance", node["contentMarkdown"])

        second_output = self.root / "generated-hierarchical-run-2"
        update_responses = iter(
            [
                response(
                    {
                        "selectedNodeIds": ["program/affine"],
                        "rationale": "Only the affine program needs refinement.",
                    },
                    4,
                ),
                response(
                    "# Follow-up assessment\n\n"
                    "## Node: program/affine\n\n"
                    "The program now includes a determinant formulation.\n",
                    5,
                ),
                response(
                    {
                        "operations": [
                            {
                                "action": "upsert",
                                "nodeId": "program/affine",
                                "parentId": "root",
                                "nodeType": "program",
                                "title": "Affine methods",
                                "summary": "Use affine invariance, scaling, and determinants.",
                                "reportSection": "## Node: program/affine",
                                "baseDigest": node["digest"],
                                "transactionIds": [head],
                            }
                        ]
                    },
                    6,
                ),
            ]
        )

        second_manifest = run_judge_bundle(
            self.root,
            "demo",
            judge,
            head,
            second_output,
            base_run=output,
            transport=lambda _: next(update_responses),
        )
        self.assertTrue(second_manifest["baseRun"].startswith("sha256:"))
        second_state = json.loads(
            (second_output / "state/state.json").read_text(encoding="utf-8")
        )
        self.assertIn("determinants", second_state["nodes"]["program/affine"]["summary"])
        self.assertEqual(second_state["nodes"]["root"]["digest"], state["nodes"]["root"]["digest"])

    def test_hierarchical_reducer_rejects_stale_node_update(self) -> None:
        state = empty_state("demo")
        root = state["nodes"]["root"]
        operation = {
            "action": "upsert",
            "nodeId": "root",
            "parentId": None,
            "nodeType": "root",
            "title": "Updated root",
            "summary": "Updated state.",
            "reportSection": "## Node: root",
            "baseDigest": "sha256:" + "0" * 64,
            "transactionIds": [],
        }
        self.assertNotEqual(operation["baseDigest"], root["digest"])
        with self.assertRaisesRegex(MathFlowError, "stale knowledge delta"):
            apply_deltas(
                state,
                ["root"],
                [operation],
                "sha256:" + "1" * 64,
                "## Node: root\n\nUpdated state.\n",
            )

    def test_later_evidence_retracts_past_adjudication_without_rewriting_history(self) -> None:
        original_head = self.commit_contribution(
            "claimed-proof", "# Claimed proof\n\nAn argument initially believed to be complete."
        )
        judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-hierarchical-markdown-v2.json"
        )
        first_output = self.root / "revision-aware-run-1"

        def response(content: object, index: int) -> dict[str, object]:
            rendered = content if isinstance(content, str) else json.dumps(content)
            return {
                "id": f"revision-generation-{index}",
                "model": "openai/gpt-5-mini",
                "choices": [{"message": {"content": rendered}}],
            }

        first_responses = iter(
            [
                response(
                    {
                        "selectedNodeIds": ["root"],
                        "rationale": "The claimed proof needs an initial adjudication.",
                    },
                    1,
                ),
                response(
                    "# Initial assessment\n\n"
                    "## Node: claim/original\n\n"
                    "The argument is accepted on the currently supplied evidence.\n",
                    2,
                ),
                response(
                    {
                        "operations": [
                            {
                                "action": "issue",
                                "adjudicationId": "claim/original",
                                "nodeId": "claim/original",
                                "parentId": "root",
                                "nodeType": "claim",
                                "title": "Original claim",
                                "summary": "Accepted on the initially supplied argument.",
                                "reportSection": "## Node: claim/original",
                                "baseDigest": None,
                                "baseRevisionId": None,
                                "subjects": [
                                    {"kind": "transaction", "id": original_head}
                                ],
                                "evidence": [
                                    {
                                        "kind": "transaction",
                                        "id": original_head,
                                        "digest": None,
                                        "relation": "supports",
                                    }
                                ],
                            }
                        ]
                    },
                    3,
                ),
            ]
        )
        first_manifest = run_judge_bundle(
            self.root,
            "demo",
            judge,
            original_head,
            first_output,
            transport=lambda _: next(first_responses),
        )
        self.assertEqual(
            first_manifest["outputProfile"], "math-flow/hierarchical-markdown-v2"
        )
        self.assertIn(
            "adjudication-revisions",
            {item["role"] for item in first_manifest["artifacts"]},
        )
        first_state = json.loads(
            (first_output / "state/state.json").read_text(encoding="utf-8")
        )
        original_node = first_state["nodes"]["claim/original"]
        self.assertEqual(original_node["status"], "active")
        first_revision_lines = (
            first_output / "state/revisions.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(first_revision_lines), 1)
        issued_revision = json.loads(first_revision_lines[0])
        self.assertEqual(issued_revision["action"], "issue")
        self.assertEqual(issued_revision["issuedAtLedgerHead"], original_head)
        self.assertEqual(issued_revision["subjects"][0]["ledgerPosition"], 1)

        correction_head = self.commit_contribution(
            "lean-refutation",
            "# Lean refutation\n\nA checked Lean proof derives a counterexample to the earlier claim.",
        )
        stale_retraction = {
            "action": "retract",
            "adjudicationId": "claim/original",
            "nodeId": "claim/original",
            "parentId": "root",
            "nodeType": "claim",
            "title": "Original claim",
            "summary": "Retracted after a later Lean counterexample.",
            "reportSection": "## Node: claim/original",
            "baseDigest": original_node["digest"],
            "baseRevisionId": "sha256:" + "0" * 64,
            "subjects": [{"kind": "transaction", "id": original_head}],
            "evidence": [
                {
                    "kind": "transaction",
                    "id": correction_head,
                    "digest": None,
                    "relation": "refutes",
                }
            ],
        }
        with self.assertRaisesRegex(MathFlowError, "stale adjudication revision"):
            apply_revision_deltas(
                first_state,
                [issued_revision],
                ["claim/original"],
                [stale_retraction],
                "sha256:" + "1" * 64,
                "## Node: claim/original\n\nRetracted.\n",
                correction_head,
                {original_head: 1, correction_head: 2},
            )
        second_output = self.root / "revision-aware-run-2"
        retract_responses = iter(
            [
                response(
                    {
                        "selectedNodeIds": ["claim/original"],
                        "rationale": "The later formal evidence directly refutes the old claim.",
                    },
                    4,
                ),
                response(
                    "# Reassessment after formal evidence\n\n"
                    "## Node: claim/original\n\n"
                    "The earlier acceptance is retracted because the later Lean contribution supplies a counterexample.\n",
                    5,
                ),
                response(
                    {
                        "operations": [
                            {
                                "action": "retract",
                                "adjudicationId": "claim/original",
                                "nodeId": "claim/original",
                                "parentId": "root",
                                "nodeType": "claim",
                                "title": "Original claim",
                                "summary": "Retracted after a later Lean counterexample.",
                                "reportSection": "## Node: claim/original",
                                "baseDigest": original_node["digest"],
                                "baseRevisionId": issued_revision["revisionId"],
                                "subjects": [
                                    {"kind": "transaction", "id": original_head}
                                ],
                                "evidence": [
                                    {
                                        "kind": "transaction",
                                        "id": correction_head,
                                        "digest": None,
                                        "relation": "refutes",
                                    }
                                ],
                            }
                        ]
                    },
                    6,
                ),
            ]
        )
        second_manifest = run_judge_bundle(
            self.root,
            "demo",
            judge,
            correction_head,
            second_output,
            base_run=first_output,
            transport=lambda _: next(retract_responses),
        )
        self.assertEqual(second_manifest["ledgerHead"], correction_head)
        second_state = json.loads(
            (second_output / "state/state.json").read_text(encoding="utf-8")
        )
        retracted_node = second_state["nodes"]["claim/original"]
        self.assertEqual(retracted_node["status"], "retired")
        self.assertEqual(retracted_node["subjects"][0]["id"], original_head)
        self.assertEqual(retracted_node["subjects"][0]["ledgerPosition"], 1)
        self.assertEqual(retracted_node["evidence"][0]["id"], correction_head)
        second_revision_lines = (
            second_output / "state/revisions.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(second_revision_lines[0], first_revision_lines[0])
        self.assertEqual(len(second_revision_lines), 2)
        retraction = json.loads(second_revision_lines[1])
        self.assertEqual(retraction["action"], "retract")
        self.assertEqual(retraction["baseRevisionId"], issued_revision["revisionId"])
        self.assertEqual(retraction["issuedAtLedgerHead"], correction_head)
        self.assertEqual(retraction["subjects"][0]["id"], original_head)
        self.assertEqual(retraction["evidence"][0]["id"], correction_head)

        unchanged_first_state = json.loads(
            (first_output / "state/state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(unchanged_first_state["nodes"]["claim/original"]["status"], "active")


if __name__ == "__main__":
    unittest.main()
