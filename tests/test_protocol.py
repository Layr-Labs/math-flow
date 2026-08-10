from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.artifacts import verify_bundle
from math_flow.coordination import (
    claim_due_build,
    complete_build,
    fail_build,
    publish_batch,
    record_completed_inputs,
)
from math_flow.formation import (
    _cached_stage_response,
    _normalize_new_node_ids_from_report_headings,
    run_knowledge_build_bundle,
)
from math_flow.judges import load_judge_spec, project, render_request
from math_flow.judgments import (
    detect_conflicts,
    load_judgment_bundle,
    plan_primary_judgment_coverage,
    run_primary_judgment_bundle,
    run_reconciliation_judgment_bundle,
)
from math_flow.knowledge import apply_deltas, apply_revision_deltas, empty_state
from math_flow.openrouter import format_error_message
from math_flow.repository import affected_problems, ledger, sha256_json, validate_pr, validate_tree
from math_flow.runs import run_judge_bundle
from math_flow.viewer import export_viewer_catalog, export_viewer_data
from math_flow.hierarchical import _structured_content


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, text=True
    )
    return result.stdout.strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class RepositoryValidationTests(unittest.TestCase):
    def test_knowledge_checkpoint_reuses_success_but_not_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint_dir = Path(directory)
            calls: list[str] = []

            def stopped(_: dict[str, object]) -> dict[str, object]:
                calls.append("stop")
                return {
                    "choices": [
                        {"finish_reason": "stop", "message": {"content": "{}"}}
                    ]
                }

            _, first_hit = _cached_stage_response(
                checkpoint_dir, "select", {"request": "stable"}, stopped
            )
            _, second_hit = _cached_stage_response(
                checkpoint_dir, "select", {"request": "stable"}, stopped
            )
            self.assertFalse(first_hit)
            self.assertTrue(second_hit)
            self.assertEqual(calls, ["stop"])

            def truncated(_: dict[str, object]) -> dict[str, object]:
                calls.append("length")
                return {
                    "choices": [
                        {"finish_reason": "length", "message": {"content": "{"}}
                    ]
                }

            _, first_truncated_hit = _cached_stage_response(
                checkpoint_dir, "extract", {"request": "truncated"}, truncated
            )
            _, second_truncated_hit = _cached_stage_response(
                checkpoint_dir, "extract", {"request": "truncated"}, truncated
            )
            self.assertFalse(first_truncated_hit)
            self.assertFalse(second_truncated_hit)
            self.assertEqual(calls.count("length"), 2)

    def test_new_node_id_follows_its_report_heading(self) -> None:
        delta = {
            "operations": [
                {
                    "action": "issue",
                    "adjudicationId": "missing-evidence_standard-facts",
                    "nodeId": "missing-evidence_standard-facts",
                    "parentId": "root",
                    "baseDigest": None,
                    "baseRevisionId": None,
                    "reportSection": "## Node: missing-evidence_standard-facts",
                }
            ]
        }
        normalized, records = _normalize_new_node_ids_from_report_headings(
            {"nodes": {"root": {}}},
            delta,
            {"## Node: missing-evidence/standard-facts"},
        )
        operation = normalized["operations"][0]
        self.assertEqual(operation["nodeId"], "missing-evidence/standard-facts")
        self.assertEqual(
            operation["reportSection"], "## Node: missing-evidence/standard-facts"
        )
        self.assertEqual(len(records), 2)

    def test_structured_control_accepts_one_json_code_fence(self) -> None:
        response = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": '```json\n{"findings": []}\n```'},
                }
            ]
        }
        self.assertEqual(_structured_content(response), {"findings": []})

    def test_structured_control_failure_reports_safe_shape_metadata(self) -> None:
        response = {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "not-json-sensitive-content"},
                }
            ]
        }
        with self.assertRaisesRegex(
            MathFlowError,
            r"finish_reason=length, content_chars=26, line=1, column=1",
        ) as raised:
            _structured_content(response)
        self.assertNotIn("sensitive-content", str(raised.exception))

    def test_current_tree_is_valid(self) -> None:
        root = Path(__file__).parents[1]
        self.assertEqual(validate_tree(root), {"problems": 1, "contributions": 3})

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
        self.assertEqual(state["problemLedgerHead"], head)
        self.assertRegex(state["problemLedgerDigest"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(state["transactions"][0]["transactionId"], head)
        self.assertEqual(state["transactions"][0]["ordinal"], 1)

    def test_affected_problems_are_scoped_unless_shared_inputs_change(self) -> None:
        write(self.root / "problems/other/problem.md", "# Other\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add other problem")
        two_problem_head = git(self.root, "rev-parse", "HEAD")

        demo_head = self.commit_contribution("first-proof")
        scoped = affected_problems(
            self.root,
            two_problem_head,
            demo_head,
            ["math_flow/**", "protocol/judges/baseline-v1.json"],
        )
        self.assertEqual(scoped["problems"], ["demo"])
        self.assertEqual(scoped["reason"], "problem-path")
        demo_digest = ledger(self.root, "demo", demo_head)["problemLedgerDigest"]

        write(self.root / "math_flow/runtime.py", "# shared runner change\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Change shared runner")
        shared_head = git(self.root, "rev-parse", "HEAD")
        shared = affected_problems(
            self.root,
            demo_head,
            shared_head,
            ["math_flow/**", "protocol/judges/baseline-v1.json"],
        )
        self.assertEqual(shared["problems"], ["demo", "other"])
        self.assertEqual(shared["reason"], "shared-input")
        after_shared_change = ledger(self.root, "demo", shared_head)
        self.assertEqual(after_shared_change["problemLedgerDigest"], demo_digest)
        self.assertEqual(after_shared_change["problemLedgerHead"], demo_head)

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

    def test_parallel_judgments_trigger_conflict_and_coalesced_knowledge_build(self) -> None:
        supporting_head = self.commit_contribution(
            "supporting-proof", "# Supporting proof\n\nA proposed proof of the claim."
        )
        refuting_head = self.commit_contribution(
            "counterexample", "# Counterexample\n\nA proposed counterexample to the claim."
        )
        judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-judgment-v1.json"
        )

        def transport_for(subject: str, stance: str):
            responses = iter(
                [
                    {
                        "id": f"report-{stance}",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": f"# Assessment\n\nThe evidence {stance} the claim in detail."
                                }
                            }
                        ],
                    },
                    {
                        "id": f"extract-{stance}",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "findings": [
                                                {
                                                    "claimKey": "demo/main-claim",
                                                    "stance": stance,
                                                    "summary": f"The subject {stance} the main claim.",
                                                    "subjectTransactionIds": [subject],
                                                    "evidenceTransactionIds": [subject],
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
            return lambda _: next(responses)

        supporting_bundle = self.root / "judgment-supporting"
        refuting_bundle = self.root / "judgment-refuting"
        run_primary_judgment_bundle(
            self.root,
            "demo",
            judge,
            refuting_head,
            [supporting_head],
            supporting_bundle,
            transport=transport_for(supporting_head, "supports"),
        )
        run_primary_judgment_bundle(
            self.root,
            "demo",
            judge,
            refuting_head,
            [refuting_head],
            refuting_bundle,
            context_transaction_ids=[supporting_head],
            transport=transport_for(refuting_head, "refutes"),
        )
        _, supporting, supporting_run_digest = load_judgment_bundle(supporting_bundle)
        _, refuting, refuting_run_digest = load_judgment_bundle(refuting_bundle)
        self.assertNotEqual(supporting["judgmentId"], refuting["judgmentId"])
        self.assertEqual(
            [item["id"] for item in refuting["subjects"]], [refuting_head]
        )

        conflicts = detect_conflicts([supporting_bundle, refuting_bundle])
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["claimKey"], "demo/main-claim")
        self.assertEqual(
            {item["stance"] for item in conflicts[0]["judgments"]},
            {"supports", "refutes"},
        )

        reconciliation_responses = iter(
            [
                {
                    "id": "reconciliation-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Reconciliation\n\nThe supplied evidence leaves the conflict unresolved."
                            }
                        }
                    ],
                },
                {
                    "id": "reconciliation-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "outcome": "unresolved",
                                        "summary": "Neither side is yet decisive.",
                                        "findings": [
                                            {
                                                "claimKey": "demo/main-claim",
                                                "stance": "uncertain",
                                                "summary": "The conflict remains open.",
                                                "subjectTransactionIds": [
                                                    supporting_head,
                                                    refuting_head,
                                                ],
                                                "evidenceTransactionIds": [
                                                    supporting_head,
                                                    refuting_head,
                                                ],
                                            }
                                        ],
                                    }
                                )
                            }
                        }
                    ],
                },
            ]
        )
        reconciliation_bundle = self.root / "judgment-reconciliation"
        run_reconciliation_judgment_bundle(
            self.root,
            "demo",
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-reconciliation-v1.json",
            refuting_head,
            conflicts[0],
            [supporting_bundle, refuting_bundle],
            reconciliation_bundle,
            transport=lambda _: next(reconciliation_responses),
        )
        _, reconciliation, reconciliation_run_digest = load_judgment_bundle(
            reconciliation_bundle
        )
        self.assertEqual(reconciliation["judgmentKind"], "reconciliation")
        self.assertEqual(reconciliation["reconciliation"]["outcome"], "unresolved")
        self.assertEqual(
            set(reconciliation["reconciliation"]["inputJudgmentIds"]),
            {supporting["judgmentId"], refuting["judgmentId"]},
        )

        builder_path = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-knowledge-builder-v1.json"
        )
        builder_digest = f"sha256:{sha256_json(load_judge_spec(builder_path))}"
        formation_scheduler = self.root / "coordination/formation-scheduler.json"
        formation_lane = record_completed_inputs(
            formation_scheduler,
            "demo",
            builder_digest,
            [
                supporting["judgmentId"],
                refuting["judgmentId"],
                reconciliation["judgmentId"],
            ],
            [conflicts[0]["conflictId"]],
            minimum_interval_seconds=60,
            now=100,
        )
        formation_claim = claim_due_build(
            formation_scheduler, formation_lane["laneId"], 100, 500
        )
        self.assertIsNotNone(formation_claim)
        conflicts_path = self.root / "coordination/conflicts.json"
        write(
            conflicts_path,
            json.dumps({"schemaVersion": 1, "conflicts": conflicts}) + "\n",
        )

        formation_response_values = [
                {
                    "id": "formation-selection",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "selectedNodeIds": ["root"],
                                        "rationale": "The unresolved claim needs a dispute node.",
                                    }
                                )
                            }
                        }
                    ],
                },
                {
                    "id": "formation-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Knowledge formation\n\n"
                                "## Node: disputes/main-claim\n\n"
                                "The immutable reconciliation leaves the opposed judgments unresolved. "
                                "This node records their provenance without choosing a side.\n"
                            }
                        }
                    ],
                },
                {
                    "id": "formation-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "operations": [
                                            {
                                                "action": "issue",
                                                "adjudicationId": "disputes/main-claim",
                                                "nodeId": "disputes/main-claim",
                                                "parentId": "root",
                                                "nodeType": "dispute",
                                                "title": "Main claim dispute",
                                                "summary": "Opposed judgments remain unresolved.",
                                                "reportSection": "## Node: disputes/main-claim",
                                                "baseDigest": None,
                                                "baseRevisionId": None,
                                                "subjects": [
                                                    {"kind": "transaction", "id": supporting_head},
                                                    {"kind": "transaction", "id": refuting_head},
                                                ],
                                                "evidence": [
                                                    {
                                                        "kind": "conflict",
                                                        "id": conflicts[0]["conflictId"],
                                                        "digest": conflicts[0]["conflictId"],
                                                        "relation": "context",
                                                    },
                                                    {
                                                        "kind": "judgment",
                                                        "id": reconciliation["judgmentId"],
                                                        "digest": reconciliation["judgmentId"],
                                                        "relation": "qualifies",
                                                    },
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
        invalid_extract = copy.deepcopy(formation_response_values[-1])
        invalid_extract["id"] = "formation-extract-invalid-heading"
        invalid_delta = json.loads(invalid_extract["choices"][0]["message"]["content"])
        invalid_delta["operations"][0]["nodeId"] = "disputes/unreported-claim"
        invalid_delta["operations"][0]["adjudicationId"] = "disputes/unreported-claim"
        invalid_delta["operations"][0]["reportSection"] = "## Node: missing-heading"
        invalid_extract["choices"][0]["message"]["content"] = json.dumps(invalid_delta)
        formation_responses = iter(
            [*formation_response_values[:-1], invalid_extract, formation_response_values[-1]]
        )
        knowledge_bundle = self.root / "knowledge-build-1"
        formation_requests: list[dict[str, object]] = []

        def formation_transport(payload: dict[str, object]) -> dict[str, object]:
            formation_requests.append(payload)
            return next(formation_responses)

        knowledge_manifest = run_knowledge_build_bundle(
            self.root,
            "demo",
            builder_path,
            refuting_head,
            formation_claim,
            [supporting_bundle, refuting_bundle, reconciliation_bundle],
            conflicts_path,
            knowledge_bundle,
            transport=formation_transport,
        )
        self.assertEqual(len(formation_requests), 4)
        self.assertTrue(
            all(request["model"] == "openai/gpt-5.6-sol" for request in formation_requests)
        )
        self.assertTrue(
            all(request["reasoning"] == {"effort": "high"} for request in formation_requests)
        )
        self.assertIn(
            "holistic current account",
            formation_requests[1]["messages"][1]["content"],
        )
        self.assertIn(
            "corrective transaction normally belongs in evidence",
            formation_requests[2]["messages"][1]["content"],
        )
        extractor_schema = formation_requests[2]["response_format"]["json_schema"][
            "schema"
        ]
        evidence_kind_schema = extractor_schema["properties"]["operations"]["items"][
            "properties"
        ]["evidence"]["items"]["properties"]["kind"]
        self.assertEqual(
            evidence_kind_schema["enum"], ["transaction", "judgment", "conflict"]
        )
        self.assertEqual(
            len(list((self.root / ".knowledge-build-1.checkpoints").glob("*.json"))),
            3,
        )
        self.assertEqual(knowledge_manifest["runKind"], "knowledge-build")
        self.assertTrue(all(run["cacheHit"] is False for run in knowledge_manifest["providerRuns"]))
        self.assertEqual(len(knowledge_manifest["providerRuns"]), 4)
        rejected = [
            run for run in knowledge_manifest["providerRuns"]
            if run.get("validationRejected") is True
        ]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["stage"], "extract")
        self.assertEqual(
            knowledge_manifest["inputs"]["judgmentSetDigest"],
            formation_claim["judgmentSetDigest"],
        )
        knowledge_state = json.loads(
            (knowledge_bundle / "state/state.json").read_text(encoding="utf-8")
        )
        dispute = knowledge_state["nodes"]["disputes/main-claim"]
        self.assertEqual(dispute["type"], "dispute")
        self.assertEqual(dispute["evidence"][0]["id"], conflicts[0]["conflictId"])
        _, knowledge_run_digest = verify_bundle(knowledge_bundle)
        completed_formation_lane = complete_build(
            formation_scheduler,
            formation_lane["laneId"],
            formation_claim["buildToken"],
            knowledge_run_digest,
            now=120,
        )
        self.assertEqual(completed_formation_lane["latestStateRun"], knowledge_run_digest)
        viewer_data = export_viewer_data(
            self.root,
            "demo",
            refuting_head,
            [knowledge_bundle],
            judgment_dirs=[supporting_bundle, refuting_bundle, reconciliation_bundle],
        )
        self.assertEqual(viewer_data["runs"][0]["runKind"], "knowledge-build")
        self.assertIn("disputes/main-claim", viewer_data["runs"][0]["changedNodeIds"])
        self.assertEqual(len(viewer_data["judgments"]), 3)
        self.assertEqual(
            {item["judgmentId"] for item in viewer_data["judgments"]},
            {
                supporting["judgmentId"],
                refuting["judgmentId"],
                reconciliation["judgmentId"],
            },
        )
        self.assertTrue(
            all(item["reportMarkdown"].startswith("#") for item in viewer_data["judgments"])
        )
        self.assertTrue(
            all(item["record"]["judgmentId"] == item["judgmentId"] for item in viewer_data["judgments"])
        )

        scheduler = self.root / "coordination/scheduler.json"
        scheduler_builder_digest = "sha256:" + "a" * 64
        first_lane = record_completed_inputs(
            scheduler,
            "demo",
            scheduler_builder_digest,
            [supporting["judgmentId"]],
            [],
            minimum_interval_seconds=60,
            now=100,
        )
        with ThreadPoolExecutor(max_workers=2) as executor:
            attempts = list(
                executor.map(
                    lambda _: claim_due_build(
                        scheduler, first_lane["laneId"], 100, 500
                    ),
                    range(2),
                )
            )
        claimed = [attempt for attempt in attempts if attempt is not None]
        self.assertEqual(len(claimed), 1)
        first_build = claimed[0]
        self.assertEqual(first_build["judgmentIds"], [supporting["judgmentId"]])

        record_completed_inputs(
            scheduler,
            "demo",
            scheduler_builder_digest,
            [refuting["judgmentId"], reconciliation["judgmentId"]],
            [conflicts[0]["conflictId"]],
            minimum_interval_seconds=60,
            now=110,
        )
        complete_build(
            scheduler,
            first_lane["laneId"],
            first_build["buildToken"],
            "sha256:" + "b" * 64,
            now=120,
        )
        self.assertIsNone(claim_due_build(scheduler, first_lane["laneId"], 179, 500))
        second_build = claim_due_build(scheduler, first_lane["laneId"], 180, 500)
        self.assertEqual(
            second_build["judgmentIds"],
            sorted([refuting["judgmentId"], reconciliation["judgmentId"]]),
        )
        self.assertEqual(second_build["conflictIds"], [conflicts[0]["conflictId"]])
        fail_build(
            scheduler,
            first_lane["laneId"],
            second_build["buildToken"],
            now=180,
        )
        retried_build = claim_due_build(scheduler, first_lane["laneId"], 180, 500)
        self.assertEqual(retried_build["buildToken"], second_build["buildToken"])
        complete_build(
            scheduler,
            first_lane["laneId"],
            retried_build["buildToken"],
            "sha256:" + "c" * 64,
            now=190,
        )
        record_completed_inputs(
            scheduler,
            "demo",
            scheduler_builder_digest,
            [refuting["judgmentId"], reconciliation["judgmentId"]],
            [conflicts[0]["conflictId"]],
            minimum_interval_seconds=60,
            now=200,
        )
        self.assertIsNone(claim_due_build(scheduler, first_lane["laneId"], 300, 500))

        projection = self.root / "projection-worktree"
        empty_coverage = plan_primary_judgment_coverage(
            self.root,
            projection,
            "demo",
            judge,
            refuting_head,
        )
        self.assertEqual(
            [item["transactionId"] for item in empty_coverage["missingTransactions"]],
            [supporting_head, refuting_head],
        )
        batch = publish_batch(
            projection,
            [
                supporting_bundle,
                refuting_bundle,
                reconciliation_bundle,
                knowledge_bundle,
            ],
        )
        self.assertEqual(len(batch["objects"]), 4)
        complete_coverage = plan_primary_judgment_coverage(
            self.root,
            projection,
            "demo",
            judge,
            refuting_head,
        )
        self.assertEqual(complete_coverage["missingTransactions"], [])
        self.assertEqual(
            complete_coverage["coveredTransactionIds"],
            sorted([supporting_head, refuting_head]),
        )
        index = json.loads(
            (projection / "indexes/problems/demo/runs.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {item["runDigest"] for item in index},
            {
                supporting_run_digest,
                refuting_run_digest,
                reconciliation_run_digest,
                knowledge_run_digest,
            },
        )
        repeated = publish_batch(
            projection,
            [
                supporting_bundle,
                refuting_bundle,
                reconciliation_bundle,
                knowledge_bundle,
            ],
        )
        self.assertEqual(repeated["batchId"], batch["batchId"])
        projection_scheduler = projection / "coordination/scheduler.json"
        write(
            projection_scheduler,
            formation_scheduler.read_text(encoding="utf-8"),
        )
        catalog = export_viewer_catalog(
            self.root,
            projection,
            "example/math-flow",
        )
        self.assertEqual(catalog["repository"]["projectionRef"], "projections")
        self.assertEqual(catalog["defaultProjectionId"], formation_lane["laneId"])
        self.assertEqual(len(catalog["projections"]), 1)
        catalog_projection = catalog["projections"][0]
        self.assertEqual(catalog_projection["latestRunDigest"], knowledge_run_digest)
        self.assertEqual(catalog_projection["runCount"], 1)
        self.assertEqual(catalog_projection["data"]["problem"]["id"], "demo")
        self.assertEqual(len(catalog_projection["data"]["judgments"]), 3)

    def test_openrouter_request_and_projection_with_fake_transport(self) -> None:
        head = self.commit_contribution("first-proof", "# Lemma\n\nA useful argument.")
        judge = Path(__file__).parents[1] / "protocol/judges/openrouter-math-review-v1.json"
        request = render_request(self.root, "demo", judge, head)
        self.assertEqual(request["model"], "openai/gpt-5.6-sol")
        self.assertEqual(request["reasoning"], {"effort": "high"})
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
                "model": "openai/gpt-5.6-sol",
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
                "model": "openai/gpt-5.6-sol",
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

    def test_v2_canonicalizes_first_root_revision_to_issue(self) -> None:
        head = self.commit_contribution("first-proof")
        judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-hierarchical-markdown-v2.json"
        )
        output = self.root / "root-normalization-run"

        def response(content: object) -> dict[str, object]:
            rendered = content if isinstance(content, str) else json.dumps(content)
            return {"choices": [{"message": {"content": rendered}}]}

        staged_responses = iter(
            [
                response(
                    {
                        "selectedNodeIds": ["root"],
                        "rationale": "The overall state should reflect the first contribution.",
                    }
                ),
                response(
                    "# Assessment\n\n"
                    "## Node: root\n\n"
                    "The research state now includes an assessed contribution.\n\n"
                    "## Node: program/top-level\n\n"
                    "A new top-level research program records the contribution.\n"
                ),
                response(
                    {
                        "operations": [
                            {
                                "action": "revise",
                                "adjudicationId": "root",
                                "nodeId": "root",
                                "parentId": None,
                                "nodeType": "root",
                                "title": "Research state for demo",
                                "summary": "The first contribution has been assessed.",
                                "reportSection": "## Node: root",
                                "baseDigest": None,
                                "baseRevisionId": None,
                                "subjects": [{"kind": "transaction", "id": head}],
                                "evidence": [
                                    {
                                        "kind": "transaction",
                                        "id": head,
                                        "digest": None,
                                        "relation": "supports",
                                    }
                                ],
                            },
                            {
                                "action": "revise",
                                "adjudicationId": "program/top-level",
                                "nodeId": "program/top-level",
                                "parentId": "None",
                                "nodeType": "program",
                                "title": "Top-level program",
                                "summary": "A program established by the first contribution.",
                                "reportSection": "## Node: program/top-level",
                                "baseDigest": "sha256:" + "0" * 64,
                                "baseRevisionId": "sha256:" + "1" * 64,
                                "subjects": [{"kind": "transaction", "id": head}],
                                "evidence": [
                                    {
                                        "kind": "transaction",
                                        "id": head,
                                        "digest": None,
                                        "relation": "supports",
                                    }
                                ],
                            },
                        ]
                    }
                ),
            ]
        )
        manifest = run_judge_bundle(
            self.root,
            "demo",
            judge,
            head,
            output,
            transport=lambda _: next(staged_responses),
        )
        delta = json.loads((output / "state/delta.json").read_text(encoding="utf-8"))
        self.assertEqual(delta["operations"][0]["action"], "issue")
        normalizations = json.loads(
            (output / "control/normalizations.json").read_text(encoding="utf-8")
        )
        normalization_kinds = {
            item["kind"] for item in normalizations["normalizations"]
        }
        self.assertTrue(
            {
                "structural-root-first-adjudication",
                "new-node-first-adjudication",
                "new-node-null-base",
                "top-level-node-parent",
            }
            <= normalization_kinds
        )
        state = json.loads((output / "state/state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["nodes"]["root"]["currentAdjudication"]["revisionNumber"], 1)
        self.assertEqual(state["nodes"]["program/top-level"]["parentId"], "root")
        self.assertEqual(delta["operations"][1]["action"], "issue")
        self.assertIn(
            "adapter-normalizations",
            {item["role"] for item in manifest["artifacts"]},
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
                "model": "openai/gpt-5.6-sol",
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

        viewer = export_viewer_data(
            self.root,
            "demo",
            correction_head,
            [first_output, second_output],
        )
        self.assertEqual(viewer["latestRunId"], "revision-aware-run-2")
        self.assertEqual(len(viewer["transactions"]), 2)
        self.assertEqual(len(viewer["runs"]), 2)
        self.assertEqual(viewer["runs"][0]["revisionIds"], [issued_revision["revisionId"]])
        self.assertEqual(viewer["runs"][1]["addedRevisionIds"], [retraction["revisionId"]])
        self.assertEqual(viewer["runs"][1]["changedNodeIds"], ["claim/original"])


if __name__ == "__main__":
    unittest.main()
