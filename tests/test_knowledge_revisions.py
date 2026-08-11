from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import load_manifest, read_verified_artifact
from math_flow.coordination import claim_due_build, record_completed_inputs
from math_flow.errors import MathFlowError
from math_flow.formation import (
    _load_base_knowledge_revision_state,
    run_knowledge_build_bundle,
)
from math_flow.judges import load_judge_spec
from math_flow.judgments import load_judgment_bundle, run_primary_judgment_bundle
from math_flow.knowledge import (
    _knowledge_revision_id,
    _with_node_digest,
    _with_state_digest,
    apply_knowledge_revision_deltas,
    empty_state_v2,
    empty_state_v3,
    validate_knowledge_revisions,
    validate_state_v2,
    validate_state_v3,
)
from math_flow.repository import sha256_json


DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64
DIGEST_C = "sha256:" + "c" * 64
TRANSACTION = "transaction-1"


def operation(
    *,
    action: str,
    node_id: str,
    parent_id: str | None,
    node_type: str,
    title: str,
    summary: str,
    base_digest: str | None,
    base_revision_id: str | None,
    subjects: list[dict[str, str]] | None = None,
    evidence: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "action": action,
        "nodeId": node_id,
        "parentId": parent_id,
        "nodeType": node_type,
        "title": title,
        "summary": summary,
        "reportSection": f"## Node: {node_id}",
        "changeSection": f"## Change: {node_id}",
        "baseDigest": base_digest,
        "baseRevisionId": base_revision_id,
        "subjects": subjects or [],
        "evidence": evidence or [],
    }


class NeutralKnowledgeRevisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.positions = {TRANSACTION: 1}
        state = empty_state_v3("demo")
        root = state["nodes"]["root"]
        state, revisions = apply_knowledge_revision_deltas(
            state,
            [],
            ["root"],
            [
                operation(
                    action="create",
                    node_id="root",
                    parent_id=None,
                    node_type="root",
                    title="Demo research state",
                    summary="Current demo state.",
                    base_digest=root["digest"],
                    base_revision_id=None,
                ),
                operation(
                    action="create",
                    node_id="program/a",
                    parent_id="root",
                    node_type="program",
                    title="Program A",
                    summary="Program A summary.",
                    base_digest=None,
                    base_revision_id=None,
                    subjects=[{"kind": "transaction", "id": TRANSACTION}],
                ),
            ],
            DIGEST_A,
            "## Node: root\nRoot body.\n\n## Change: root\nInitialized the research state.\n\n## Node: program/a\nA body.\n\n## Change: program/a\nCreated the program from its first supported contribution.\n",
            TRANSACTION,
            self.positions,
        )
        self.state = state
        self.revisions = revisions

    def test_create_uses_neutral_pointer_and_all_initial_facets(self) -> None:
        validate_state_v3(self.state, self.revisions, "demo")
        node = self.state["nodes"]["program/a"]
        self.assertEqual(
            self.revisions[-1]["facets"],
            ["topology", "content", "lifecycle", "provenance"],
        )
        self.assertEqual(set(node["currentRevision"]), {"revisionId", "revisionNumber"})
        self.assertNotIn("adjudicationId", self.revisions[-1])
        self.assertNotIn("currentAdjudication", node)
        self.assertEqual(
            self.revisions[-1]["changeRationale"],
            "Created the program from its first supported contribution.",
        )
        self.assertEqual(
            self.revisions[-1]["changeRef"],
            {
                "artifact": "report.md",
                "digest": DIGEST_A,
                "section": "## Change: program/a",
            },
        )

    def test_reducer_derives_a_genuine_topology_only_revision(self) -> None:
        prior = self.state["nodes"]["program/a"]
        state, revisions = apply_knowledge_revision_deltas(
            self.state,
            self.revisions,
            ["root", "program/a"],
            [
                operation(
                    action="create",
                    node_id="program/parent",
                    parent_id="root",
                    node_type="program",
                    title="Parent program",
                    summary="Parent summary.",
                    base_digest=None,
                    base_revision_id=None,
                ),
                operation(
                    action="update",
                    node_id="program/a",
                    parent_id="program/parent",
                    node_type="program",
                    title=prior["title"],
                    summary=prior["summary"],
                    base_digest=prior["digest"],
                    base_revision_id=prior["currentRevision"]["revisionId"],
                    subjects=[{"kind": "transaction", "id": TRANSACTION}],
                ),
            ],
            DIGEST_B,
            "## Node: program/parent\nParent body.\n\n## Change: program/parent\nCreated a durable parent program.\n\n## Node: program/a\nA body.\n\n## Change: program/a\nMoved the program under its durable parent.\n",
            "ledger-head-2",
            self.positions,
        )
        self.assertEqual(revisions[-1]["facets"], ["topology"])
        self.assertEqual(state["nodes"]["program/a"]["parentId"], "program/parent")

    def test_content_lifecycle_and_provenance_cannot_hide_as_topology_only(self) -> None:
        prior = self.state["nodes"]["program/a"]
        state, revisions = apply_knowledge_revision_deltas(
            self.state,
            self.revisions,
            ["program/a"],
            [
                operation(
                    action="retire",
                    node_id="program/a",
                    parent_id="root",
                    node_type="method",
                    title="Former program A",
                    summary="Program A is no longer active.",
                    base_digest=prior["digest"],
                    base_revision_id=prior["currentRevision"]["revisionId"],
                    evidence=[
                        {
                            "kind": "transaction",
                            "id": TRANSACTION,
                            "digest": None,
                            "relation": "context",
                        }
                    ],
                )
            ],
            DIGEST_C,
            "## Node: program/a\nRetired body.\n\n## Change: program/a\nRetired the program after contrary evidence.\n",
            "ledger-head-3",
            self.positions,
        )
        self.assertEqual(
            revisions[-1]["facets"],
            ["topology", "content", "lifecycle", "provenance"],
        )
        validate_state_v3(state, revisions, "demo")

        dishonest = copy.deepcopy(revisions)
        dishonest[-1]["facets"] = ["topology"]
        dishonest[-1]["revisionId"] = _knowledge_revision_id(dishonest[-1])
        with self.assertRaisesRegex(
            MathFlowError, "facets do not match changed fields"
        ):
            validate_knowledge_revisions(dishonest, "demo")

    def test_report_pointer_only_update_is_rejected_as_a_no_op(self) -> None:
        prior = self.state["nodes"]["program/a"]
        with self.assertRaisesRegex(MathFlowError, "makes no material change"):
            apply_knowledge_revision_deltas(
                self.state,
                self.revisions,
                ["program/a"],
                [
                    operation(
                        action="update",
                        node_id="program/a",
                        parent_id="root",
                        node_type="program",
                        title=prior["title"],
                        summary=prior["summary"],
                        base_digest=prior["digest"],
                        base_revision_id=prior["currentRevision"]["revisionId"],
                        subjects=[{"kind": "transaction", "id": TRANSACTION}],
                    )
                ],
                DIGEST_B,
                "## Node: program/a\nA body.\n\n## Change: program/a\nReviewed the node without finding a material change.\n",
                "ledger-head-2",
                self.positions,
            )

    def test_change_rationale_requires_one_exact_change_section(self) -> None:
        prior = self.state["nodes"]["program/a"]
        with self.assertRaisesRegex(MathFlowError, "missing or ambiguous"):
            apply_knowledge_revision_deltas(
                self.state,
                self.revisions,
                ["program/a"],
                [
                    operation(
                        action="update",
                        node_id="program/a",
                        parent_id="root",
                        node_type="program",
                        title=prior["title"],
                        summary="A materially updated summary.",
                        base_digest=prior["digest"],
                        base_revision_id=prior["currentRevision"]["revisionId"],
                        subjects=[{"kind": "transaction", "id": TRANSACTION}],
                    )
                ],
                DIGEST_B,
                "## Node: program/a\nUpdated body.\n\n## Change: program/a\nFirst rationale.\n\n## Change: program/a\nSecond rationale.\n",
                "ledger-head-2",
                self.positions,
            )

    def test_v2_state_remains_readable(self) -> None:
        old_state = empty_state_v2("demo")
        validated, revisions = validate_state_v2(old_state, [], "demo")
        self.assertEqual(validated["schemaVersion"], 2)
        self.assertEqual(revisions, [])
        self.assertIn("currentAdjudication", validated["nodes"]["root"])

    def test_unrevised_root_must_remain_the_canonical_seed(self) -> None:
        state = empty_state_v3("demo")
        state["nodes"]["root"]["summary"] = "Invented knowledge without a revision."
        state["nodes"]["root"] = _with_node_digest(state["nodes"]["root"])
        state = _with_state_digest(state)
        with self.assertRaisesRegex(MathFlowError, "canonical seed"):
            validate_state_v3(state, [], "demo")

    def test_v2_builder_serializes_and_reloads_neutral_artifacts(self) -> None:
        repository_root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.name", "Test Author"], cwd=root, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=root,
                check=True,
            )
            problem = root / "problems/demo/problem.md"
            problem.parent.mkdir(parents=True)
            problem.write_text("# Demo\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "Create problem"], cwd=root, check=True
            )
            contribution = root / "problems/demo/contributions/proof/README.md"
            contribution.parent.mkdir(parents=True)
            contribution.write_text("# Claim\n\nA proof.", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "Add proof"], cwd=root, check=True
            )
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.strip()

            judge_path = (
                repository_root
                / "protocol/judges/openrouter-markdown-judgment-v1.json"
            )
            judgment_responses = iter(
                [
                    {
                        "id": "report",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {"message": {"content": "# Assessment\n\nThe claim is supported."}}
                        ],
                    },
                    {
                        "id": "extract",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "findings": [
                                                {
                                                    "claimKey": "demo/claim",
                                                    "stance": "supports",
                                                    "summary": "The claim is supported.",
                                                    "subjectTransactionIds": [head],
                                                    "evidenceTransactionIds": [head],
                                                }
                                            ]
                                        }
                                    )
                                }
                            }
                        ],
                    },
                ]
            )
            judgment_dir = root / "judgment"
            run_primary_judgment_bundle(
                root,
                "demo",
                judge_path,
                head,
                [head],
                judgment_dir,
                transport=lambda _: next(judgment_responses),
            )
            _, judgment, _ = load_judgment_bundle(judgment_dir)

            builder_path = (
                repository_root
                / "protocol/judges/openrouter-research-program-builder-v2.json"
            )
            builder_digest = f"sha256:{sha256_json(load_judge_spec(builder_path))}"
            scheduler = root / "scheduler.json"
            lane = record_completed_inputs(
                scheduler,
                "demo",
                builder_digest,
                [judgment["judgmentId"]],
                [],
                0,
                1,
            )
            claim = claim_due_build(scheduler, lane["laneId"], 1, 10)
            self.assertIsNotNone(claim)

            formation_responses = iter(
                [
                    {
                        "id": "select",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "selectedNodeIds": ["root"],
                                            "rationale": "Create a durable program.",
                                        }
                                    )
                                }
                            }
                        ],
                    },
                    {
                        "id": "report",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": "# Formation\n\n## Node: program/main\nMain program body.\n\n## Change: program/main\nCreated a durable program from the supported claim.\n"
                                }
                            }
                        ],
                    },
                    {
                        "id": "extract",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "operations": [
                                                {
                                                    "action": "create",
                                                    "nodeId": "program/main",
                                                    "parentId": "root",
                                                    "nodeType": "program",
                                                    "title": "Main program",
                                                    "summary": "The main research program.",
                                                    "reportSection": "## Node: program/main",
                                                    "changeSection": "## Change: program/main",
                                                    "baseDigest": None,
                                                    "baseRevisionId": None,
                                                    "subjects": [
                                                        {"kind": "transaction", "id": head}
                                                    ],
                                                    "evidence": [
                                                        {
                                                            "kind": "judgment",
                                                            "id": judgment["judgmentId"],
                                                            "digest": judgment["judgmentId"],
                                                            "relation": "supports",
                                                        }
                                                    ],
                                                }
                                            ]
                                        }
                                    )
                                }
                            }
                        ],
                    },
                ]
            )
            output = root / "knowledge"
            formation_requests: list[dict[str, object]] = []

            def formation_transport(payload: dict[str, object]) -> dict[str, object]:
                formation_requests.append(payload)
                return next(formation_responses)

            manifest = run_knowledge_build_bundle(
                root,
                "demo",
                builder_path,
                head,
                claim,
                [judgment_dir],
                None,
                output,
                transport=formation_transport,
            )
            self.assertEqual(
                manifest["outputProfile"], "math-flow/knowledge-build-markdown-v2"
            )
            self.assertIn(
                "knowledge-revisions",
                {item["role"] for item in manifest["artifacts"]},
            )
            self.assertNotIn(
                "adjudication-revisions",
                {item["role"] for item in manifest["artifacts"]},
            )
            operation_schema = formation_requests[2]["response_format"][
                "json_schema"
            ]["schema"]["properties"]["operations"]["items"]
            self.assertEqual(
                operation_schema["properties"]["action"]["enum"],
                ["create", "update", "retire", "restore"],
            )
            self.assertNotIn("adjudicationId", operation_schema["properties"])
            self.assertNotIn("facets", operation_schema["properties"])
            self.assertIn("changeSection", operation_schema["properties"])
            self.assertNotIn("changeRationale", operation_schema["properties"])
            self.assertIn(
                "Do not classify revision facets",
                formation_requests[2]["messages"][1]["content"],
            )
            stored_manifest, stored_digest = load_manifest(output)
            state = json.loads(
                read_verified_artifact(output, stored_manifest, "knowledge-state")
            )
            revision_text = read_verified_artifact(
                output, stored_manifest, "knowledge-revisions"
            ).decode("utf-8")
            revisions = [json.loads(line) for line in revision_text.splitlines()]
            self.assertEqual(state["schemaVersion"], 3)
            self.assertEqual(revisions[-1]["action"], "create")
            self.assertEqual(
                revisions[-1]["facets"],
                ["topology", "content", "lifecycle", "provenance"],
            )
            self.assertEqual(
                revisions[-1]["changeRationale"],
                "Created a durable program from the supported claim.",
            )
            self.assertEqual(
                revisions[-1]["changeRef"]["section"],
                "## Change: program/main",
            )
            self.assertIn(
                "changeSection must exactly equal `## Change: <nodeId>`",
                formation_requests[2]["messages"][1]["content"],
            )
            loaded_state, loaded_revisions, base_digest, base_head = (
                _load_base_knowledge_revision_state(output, "demo")
            )
            self.assertEqual(loaded_state, state)
            self.assertEqual(loaded_revisions, revisions)
            self.assertEqual(base_digest, stored_digest)
            self.assertEqual(base_head, head)


if __name__ == "__main__":
    unittest.main()
