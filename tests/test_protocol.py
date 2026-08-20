from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from math_flow.errors import MathFlowError
from math_flow.cli import main
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
    plan_primary_judgment_inputs,
    plan_primary_judgment_coverage,
    plan_reconciliation_inputs,
    run_primary_judgment_bundle,
    run_reconciliation_judgment_bundle,
    verify_primary_judgment_artifacts,
)
from math_flow.knowledge import apply_deltas, apply_revision_deltas, empty_state
from math_flow.openrouter import format_error_message
from math_flow.repository import affected_problems, ledger, sha256_json, validate_pr, validate_tree
from math_flow.runs import run_judge_bundle
from math_flow.viewer import (
    _projection_catalog_sort_key,
    export_viewer_catalog,
    export_viewer_data,
)
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
    def test_viewer_source_prefers_active_projection_lanes(self) -> None:
        retired = {
            "id": "retired",
            "problemId": "demo",
            "label": "a-retired-builder",
            "projectionSpec": None,
        }
        active = {
            "id": "active",
            "problemId": "demo",
            "label": "z-active-projection",
            "projectionSpec": {"digest": "sha256:" + "a" * 64},
        }
        self.assertEqual(
            sorted([retired, active], key=_projection_catalog_sort_key),
            [active, retired],
        )

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

    def test_knowledge_checkpoint_retries_and_does_not_cache_empty_responses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint_dir = Path(directory)
            calls: list[str] = []

            def eventually_succeeds(_: dict[str, object]) -> dict[str, object]:
                calls.append("send")
                content = "{}" if len(calls) == 3 else ""
                return {
                    "choices": [
                        {"finish_reason": "stop", "message": {"content": content}}
                    ]
                }

            response, first_hit = _cached_stage_response(
                checkpoint_dir, "report", {"request": "retry"}, eventually_succeeds
            )
            cached_response, second_hit = _cached_stage_response(
                checkpoint_dir, "report", {"request": "retry"}, eventually_succeeds
            )
            self.assertFalse(first_hit)
            self.assertTrue(second_hit)
            self.assertEqual(response, cached_response)
            self.assertEqual(calls, ["send", "send", "send"])

            empty_calls: list[str] = []

            def always_empty(_: dict[str, object]) -> dict[str, object]:
                empty_calls.append("send")
                return {
                    "choices": [
                        {"finish_reason": "stop", "message": {"content": None}}
                    ]
                }

            _, first_empty_hit = _cached_stage_response(
                checkpoint_dir, "extract", {"request": "empty"}, always_empty
            )
            _, second_empty_hit = _cached_stage_response(
                checkpoint_dir, "extract", {"request": "empty"}, always_empty
            )
            self.assertFalse(first_empty_hit)
            self.assertFalse(second_empty_hit)
            self.assertEqual(len(empty_calls), 6)

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
        summary = validate_tree(root)
        self.assertEqual(
            set(summary),
            {"problems", "contributions", "researchDirections", "directionEvents"},
        )
        for count in summary.values():
            self.assertIsInstance(count, int)
            self.assertGreaterEqual(count, 0)

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

    def test_claim_manifest_may_reference_only_prior_canonical_transactions(self) -> None:
        prior = self.commit_contribution("prior")
        base = prior
        contribution = self.root / "problems/demo/contributions/declared"
        write(contribution / "README.md", "## Claim\n\nA declared claim.\n")
        write(
            contribution / "claims.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "claims": [
                        {
                            "claimKey": "demo/declared-claim",
                            "statement": "A declared claim.",
                            "dependencyTransactionIds": [prior],
                        }
                    ],
                }
            ),
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Add declared claim")
        head = git(self.root, "rev-parse", "HEAD")
        self.assertEqual(validate_pr(self.root, base, head)["contributionId"], "declared")

        invalid_temporary = tempfile.TemporaryDirectory()
        self.addCleanup(invalid_temporary.cleanup)
        invalid_root = Path(invalid_temporary.name)
        git(invalid_root, "init", "-q")
        git(invalid_root, "config", "user.name", "Test Author")
        git(invalid_root, "config", "user.email", "test@example.com")
        write(invalid_root / "problems/demo/problem.md", "# Demo\n")
        git(invalid_root, "add", ".")
        git(invalid_root, "commit", "-qm", "Create problem")
        invalid_base = git(invalid_root, "rev-parse", "HEAD")
        invalid = invalid_root / "problems/demo/contributions/invalid"
        write(invalid / "README.md", "## Claim\n\nInvalid dependency.\n")
        write(
            invalid / "claims.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "claims": [
                        {
                            "claimKey": "demo/invalid",
                            "statement": "Invalid dependency.",
                            "dependencyTransactionIds": ["f" * 40],
                        }
                    ],
                }
            ),
        )
        git(invalid_root, "add", ".")
        git(invalid_root, "commit", "-qm", "Add invalid claim")
        invalid_head = git(invalid_root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(MathFlowError, "not a prior canonical transaction"):
            validate_pr(invalid_root, invalid_base, invalid_head)

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

    def test_flat_downloaded_judgment_artifact_can_resume_after_unrelated_commit(self) -> None:
        subject = self.commit_contribution(
            "resume-proof", "# Resume proof\n\nEvidence for a resumable judgment."
        )
        judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-judgment-v1.json"
        )
        responses = iter(
            [
                {
                    "id": "resume-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Assessment\n\nThe submitted evidence supports the claim."
                            }
                        }
                    ],
                },
                {
                    "id": "resume-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "findings": [
                                            {
                                                "claimKey": "demo/resume-claim",
                                                "stance": "supports",
                                                "summary": "The evidence supports the claim.",
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
        downloaded = tempfile.TemporaryDirectory()
        self.addCleanup(downloaded.cleanup)
        flat_download = Path(downloaded.name)
        run_primary_judgment_bundle(
            self.root,
            "demo",
            judge,
            subject,
            [subject],
            flat_download,
            transport=lambda _: next(responses),
        )

        write(self.root / "docs/maintenance.md", "Unrelated maintenance.\n")
        git(self.root, "add", "docs/maintenance.md")
        git(self.root, "commit", "-qm", "Unrelated maintenance")
        resumed_head = git(self.root, "rev-parse", "HEAD")
        verified = verify_primary_judgment_artifacts(
            self.root,
            flat_download,
            "demo",
            judge,
            resumed_head,
            [subject],
        )
        self.assertEqual(verified["ledgerHead"], resumed_head)
        self.assertEqual(len(verified["bundles"]), 1)
        self.assertEqual(verified["bundles"][0]["path"], str(flat_download.resolve()))
        self.assertEqual(
            verified["bundles"][0]["subjectTransactionIds"], [subject]
        )

        self.commit_contribution("later-proof")
        with self.assertRaisesRegex(MathFlowError, "stale for the current problem ledger"):
            verify_primary_judgment_artifacts(
                self.root,
                flat_download,
                "demo",
                judge,
                "HEAD",
                [subject],
            )

    def test_validity_judgment_is_one_per_claim_and_uses_only_declared_dependencies(self) -> None:
        dependency = self.commit_contribution(
            "premise", "# Premise\n\nA previously established lemma."
        )
        unrelated = self.commit_contribution(
            "unrelated", "# Unrelated\n\nThis material is outside the dependency boundary."
        )
        subject = self.commit_contribution(
            "subject",
            "\n".join(
                [
                    "# Subject",
                    "",
                    "## Claim",
                    "",
                    f"The declared result follows from transaction {dependency}.",
                ]
            ),
        )
        repository_root = Path(__file__).parents[1]
        spec = json.loads(
            (
                repository_root
                / "protocol/judges/openrouter-validity-judgment-v2.json"
            ).read_text(encoding="utf-8")
        )
        spec.pop("contextProjection")
        judge = self.root / "validity-judge.json"
        write(judge, json.dumps(spec))
        requests: list[dict[str, object]] = []
        responses = iter(
            [
                {
                    "id": "validity-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": "## demo/subject\n\nThe argument is valid under its cited premise."
                            },
                        }
                    ],
                },
                {
                    "id": "validity-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {
                                "content": json.dumps(
                                    {
                                        "assessments": [
                                            {
                                                "claimKey": "demo/subject",
                                                "status": "valid",
                                                "premiseStatus": "satisfied",
                                                "summary": "The cited premise establishes the claim.",
                                                "scopeQualifications": [],
                                                "evidenceIssues": [],
                                                "evidenceTransactionIds": [dependency],
                                            }
                                        ]
                                    }
                                )
                            },
                        }
                    ],
                },
            ]
        )

        def transport(request: dict[str, object]) -> dict[str, object]:
            requests.append(request)
            return next(responses)

        bundle = self.root / "validity-bundle"
        run_primary_judgment_bundle(
            self.root,
            "demo",
            judge,
            subject,
            [subject],
            bundle,
            transport=transport,
        )
        manifest, judgment, _ = load_judgment_bundle(bundle)
        self.assertEqual(manifest["outputProfile"], "math-flow/validity-judgment-v2")
        self.assertEqual(len(judgment["assessments"]), 1)
        self.assertEqual(len(judgment["findings"]), 1)
        self.assertEqual(judgment["findings"][0]["stance"], "supports")
        packet = json.loads(
            (bundle / "dependency-packet.json").read_text(encoding="utf-8")
        )
        self.assertEqual(packet["dependencyTransactionIds"], [dependency])
        report_prompt = str(requests[0]["messages"][1]["content"])
        self.assertIn(dependency, report_prompt)
        self.assertNotIn(unrelated, report_prompt)
        self.assertIn("prevent false acceptance", report_prompt)
        self.assertIn("every material proof obligation", report_prompt)
        self.assertIn("do not constrain the analysis", report_prompt)
        self.assertIn(
            "overriding priority is to prevent an incorrect or unsupported result",
            str(requests[0]["messages"][0]["content"]),
        )

        projection = self.root / "projection"
        publish_batch(projection, [bundle])
        coverage = plan_primary_judgment_coverage(
            self.root, projection, "demo", judge, subject
        )
        self.assertIn(subject, coverage["coveredTransactionIds"])

    def test_validity_judgment_rejects_truncated_report(self) -> None:
        subject = self.commit_contribution("subject", "## Claim\n\nA claim.")
        repository_root = Path(__file__).parents[1]
        spec = json.loads(
            (
                repository_root
                / "protocol/judges/openrouter-validity-judgment-v2.json"
            ).read_text(encoding="utf-8")
        )
        spec.pop("contextProjection")
        judge = self.root / "validity-judge.json"
        write(judge, json.dumps(spec))
        response = {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "## demo/subject\n\nPartial"},
                }
            ]
        }
        with self.assertRaisesRegex(MathFlowError, "report response was truncated"):
            run_primary_judgment_bundle(
                self.root,
                "demo",
                judge,
                subject,
                [subject],
                self.root / "truncated-validity-bundle",
                transport=lambda _: response,
            )

    def test_primary_publication_rejects_distinct_judgments_for_same_subject(
        self,
    ) -> None:
        subject = self.commit_contribution(
            "duplicate-subject",
            "# Claim\n\nEvidence for one transaction.",
        )
        judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-judgment-v1.json"
        )

        def build(name: str, conclusion: str) -> Path:
            responses = iter(
                [
                    {
                        "id": f"report-{name}",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": f"# Assessment\n\n{conclusion}"
                                }
                            }
                        ],
                    },
                    {
                        "id": f"extract-{name}",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "findings": [
                                                {
                                                    "claimKey": "demo/duplicate-subject",
                                                    "stance": "supports",
                                                    "summary": conclusion,
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
            output = self.root / f"judgment-{name}"
            run_primary_judgment_bundle(
                self.root,
                "demo",
                judge,
                subject,
                [subject],
                output,
                transport=lambda _: next(responses),
            )
            return output

        first = build("first", "The first rigorous assessment accepts the claim.")
        second = build("second", "A distinct rigorous assessment also accepts it.")
        _, first_judgment, _ = load_judgment_bundle(first)
        second_manifest, second_judgment, second_run_digest = load_judgment_bundle(
            second
        )
        self.assertNotEqual(
            first_judgment["judgmentId"], second_judgment["judgmentId"]
        )

        atomic_projection = self.root / "atomic-publication"
        with self.assertRaisesRegex(
            MathFlowError, "multiple distinct primary judgments"
        ):
            publish_batch(atomic_projection, [first, second])
        self.assertFalse(atomic_projection.exists())

        projection = self.root / "sequential-publication"
        publish_batch(projection, [first])
        with self.assertRaisesRegex(
            MathFlowError, "multiple distinct primary judgments"
        ):
            publish_batch(projection, [second])
        index_path = projection / "indexes/problems/demo/runs.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertEqual(len(index), 1)

        digest_hex = second_run_digest.removeprefix("sha256:")
        relative = Path("objects") / "judgment" / digest_hex[:2] / digest_hex
        shutil.copytree(second, projection / relative)
        index.append(
            {
                "runDigest": second_run_digest,
                "runKind": "judgment",
                "problemId": second_manifest["problemId"],
                "path": relative.as_posix(),
            }
        )
        write(index_path, json.dumps(index, indent=2) + "\n")
        with self.assertRaisesRegex(
            MathFlowError, "multiple distinct reusable primary judgments"
        ):
            plan_primary_judgment_coverage(
                self.root,
                projection,
                "demo",
                judge,
                subject,
                subject_transaction_id=subject,
            )

    def test_partial_matrix_artifacts_are_bounded_to_the_frozen_plan(self) -> None:
        supporting_head = self.commit_contribution(
            "partial-support", "# Support\n\nEvidence for two claims."
        )
        refuting_head = self.commit_contribution(
            "partial-refute", "# Refutation\n\nCounterevidence for two claims."
        )
        primary_judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-judgment-v1.json"
        )

        def primary_transport(subject: str, stance: str):
            responses = iter(
                [
                    {
                        "id": f"partial-report-{stance}",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": "# Assessment\n\nTwo claims were checked."
                                }
                            }
                        ],
                    },
                    {
                        "id": f"partial-extract-{stance}",
                        "model": "openai/gpt-5.6-sol",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "findings": [
                                                {
                                                    "claimKey": claim_key,
                                                    "stance": stance,
                                                    "summary": f"The subject {stance} {claim_key}.",
                                                    "subjectTransactionIds": [subject],
                                                    "evidenceTransactionIds": [subject],
                                                }
                                                for claim_key in (
                                                    "demo/partial-a",
                                                    "demo/partial-b",
                                                )
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

        supporting_bundle = self.root / "partial-primary-support"
        refuting_bundle = self.root / "partial-primary-refute"
        run_primary_judgment_bundle(
            self.root,
            "demo",
            primary_judge,
            refuting_head,
            [supporting_head],
            supporting_bundle,
            transport=primary_transport(supporting_head, "supports"),
        )
        run_primary_judgment_bundle(
            self.root,
            "demo",
            primary_judge,
            refuting_head,
            [refuting_head],
            refuting_bundle,
            transport=primary_transport(refuting_head, "refutes"),
        )

        partial_primary = verify_primary_judgment_artifacts(
            self.root,
            supporting_bundle,
            "demo",
            primary_judge,
            refuting_head,
            [supporting_head, refuting_head],
            allow_expected_subset=True,
        )
        self.assertEqual(
            partial_primary["missingExpectedSubjectTransactionIds"],
            [refuting_head],
        )
        with self.assertRaisesRegex(MathFlowError, "do not match the current plan"):
            verify_primary_judgment_artifacts(
                self.root,
                supporting_bundle,
                "demo",
                primary_judge,
                refuting_head,
                [supporting_head, refuting_head],
            )
        with self.assertRaisesRegex(MathFlowError, "outside the current plan"):
            verify_primary_judgment_artifacts(
                self.root,
                supporting_bundle,
                "demo",
                primary_judge,
                refuting_head,
                [refuting_head],
                allow_expected_subset=True,
            )

        resume_projection = self.root / "partial-resume-projection"
        publish_batch(resume_projection, [supporting_bundle])
        resume_plan = plan_primary_judgment_coverage(
            self.root,
            resume_projection,
            "demo",
            primary_judge,
            refuting_head,
        )
        self.assertEqual(
            [
                item["transactionId"]
                for item in resume_plan["missingTransactions"]
            ],
            [refuting_head],
        )
        resume_artifacts = self.root / "partial-resume-artifacts"
        shutil.copytree(supporting_bundle, resume_artifacts / "judgment-support")
        shutil.copytree(refuting_bundle, resume_artifacts / "judgment-refute")
        retained_resume = verify_primary_judgment_artifacts(
            self.root,
            resume_artifacts,
            "demo",
            primary_judge,
            refuting_head,
            [refuting_head],
            retain_expected_subset=True,
        )
        _, supporting_judgment, _ = load_judgment_bundle(supporting_bundle)
        _, refuting_judgment, _ = load_judgment_bundle(refuting_bundle)
        self.assertEqual(
            [item["judgmentId"] for item in retained_resume["bundles"]],
            [refuting_judgment["judgmentId"]],
        )
        self.assertEqual(
            [item["judgmentId"] for item in retained_resume["rejectedBundles"]],
            [supporting_judgment["judgmentId"]],
        )
        self.assertEqual(
            retained_resume["rejectedSubjectTransactionIds"],
            [supporting_head],
        )
        publish_batch(
            resume_projection,
            [Path(str(retained_resume["bundles"][0]["path"]))],
        )
        self.assertEqual(
            plan_primary_judgment_coverage(
                self.root,
                resume_projection,
                "demo",
                primary_judge,
                refuting_head,
            )["missingTransactions"],
            [],
        )

        mixed_responses = iter(
            [
                {
                    "id": "mixed-resume-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Assessment\n\nA mixed-subject bundle."
                            }
                        }
                    ],
                },
                {
                    "id": "mixed-resume-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "findings": [
                                            {
                                                "claimKey": "demo/mixed-resume",
                                                "stance": "supports",
                                                "summary": "The mixed evidence was assessed.",
                                                "subjectTransactionIds": [
                                                    supporting_head,
                                                    refuting_head,
                                                ],
                                                "evidenceTransactionIds": [
                                                    supporting_head,
                                                    refuting_head,
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
        mixed_bundle = self.root / "mixed-resume-bundle"
        run_primary_judgment_bundle(
            self.root,
            "demo",
            primary_judge,
            refuting_head,
            [supporting_head, refuting_head],
            mixed_bundle,
            transport=lambda _: next(mixed_responses),
        )
        with self.assertRaisesRegex(
            MathFlowError, "do not contain a retained planned subject"
        ):
            verify_primary_judgment_artifacts(
                self.root,
                mixed_bundle,
                "demo",
                primary_judge,
                refuting_head,
                [refuting_head],
                retain_expected_subset=True,
            )

        conflicts = {
            str(item["claimKey"]): item
            for item in detect_conflicts([supporting_bundle, refuting_bundle])
        }
        self.assertEqual(set(conflicts), {"demo/partial-a", "demo/partial-b"})
        first_conflict = conflicts["demo/partial-a"]
        second_conflict = conflicts["demo/partial-b"]
        reconciliation_judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-reconciliation-v1.json"
        )
        reconciliation_responses = iter(
            [
                {
                    "id": "partial-reconciliation-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Reconciliation\n\nThe first conflict remains open."
                            }
                        }
                    ],
                },
                {
                    "id": "partial-reconciliation-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "outcome": "unresolved",
                                        "summary": "The first conflict remains open.",
                                        "findings": [
                                            {
                                                "claimKey": "demo/partial-a",
                                                "stance": "uncertain",
                                                "summary": "Neither assessment is decisive.",
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
        reconciliation_bundle = self.root / "partial-reconciliation"
        run_reconciliation_judgment_bundle(
            self.root,
            "demo",
            reconciliation_judge,
            refuting_head,
            first_conflict,
            [supporting_bundle, refuting_bundle],
            reconciliation_bundle,
            transport=lambda _: next(reconciliation_responses),
        )
        second_reconciliation_responses = iter(
            [
                {
                    "id": "complete-reconciliation-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Reconciliation\n\nThe second conflict also remains open."
                            }
                        }
                    ],
                },
                {
                    "id": "complete-reconciliation-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "outcome": "unresolved",
                                        "summary": "The second conflict remains open.",
                                        "findings": [
                                            {
                                                "claimKey": "demo/partial-b",
                                                "stance": "uncertain",
                                                "summary": "Neither second assessment is decisive.",
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
        second_reconciliation_bundle = self.root / "complete-reconciliation"
        run_reconciliation_judgment_bundle(
            self.root,
            "demo",
            reconciliation_judge,
            refuting_head,
            second_conflict,
            [supporting_bundle, refuting_bundle],
            second_reconciliation_bundle,
            transport=lambda _: next(second_reconciliation_responses),
        )
        expected_conflicts = [
            str(first_conflict["conflictId"]),
            str(second_conflict["conflictId"]),
        ]
        partial_reconciliation = plan_reconciliation_inputs(
            self.root,
            self.root / "partial-reconciliation-projection",
            "demo",
            primary_judge,
            reconciliation_judge,
            refuting_head,
            [supporting_bundle, refuting_bundle],
            [reconciliation_bundle],
            expected_conflicts,
            allow_expected_subset=True,
        )
        self.assertEqual(
            partial_reconciliation["missingExpectedConflictIds"],
            [str(second_conflict["conflictId"])],
        )
        self.assertEqual(
            [item["conflictId"] for item in partial_reconciliation["newBundles"]],
            [str(first_conflict["conflictId"])],
        )
        with self.assertRaisesRegex(MathFlowError, "do not match the current plan"):
            plan_reconciliation_inputs(
                self.root,
                self.root / "partial-reconciliation-projection",
                "demo",
                primary_judge,
                reconciliation_judge,
                refuting_head,
                [supporting_bundle, refuting_bundle],
                [reconciliation_bundle],
                expected_conflicts,
            )
        with self.assertRaisesRegex(MathFlowError, "outside the current plan"):
            plan_reconciliation_inputs(
                self.root,
                self.root / "partial-reconciliation-projection",
                "demo",
                primary_judge,
                reconciliation_judge,
                refuting_head,
                [supporting_bundle, refuting_bundle],
                [reconciliation_bundle],
                [str(second_conflict["conflictId"])],
                allow_expected_subset=True,
            )

        overlap_projection = self.root / "overlap-reconciliation-projection"
        publish_batch(overlap_projection, [reconciliation_bundle])
        overlap_plan = plan_reconciliation_inputs(
            self.root,
            overlap_projection,
            "demo",
            primary_judge,
            reconciliation_judge,
            refuting_head,
            [supporting_bundle, refuting_bundle],
            [reconciliation_bundle, second_reconciliation_bundle],
            expected_conflicts,
            allow_expected_subset=True,
        )
        self.assertEqual(overlap_plan["missingExpectedConflictIds"], [])
        self.assertEqual(
            {str(item["conflictId"]) for item in overlap_plan["newBundles"]},
            set(expected_conflicts),
        )
        for bundle in overlap_plan["newBundles"]:
            publish_batch(overlap_projection, [Path(str(bundle["path"]))])
        completed_overlap = plan_reconciliation_inputs(
            self.root,
            overlap_projection,
            "demo",
            primary_judge,
            reconciliation_judge,
            refuting_head,
            [supporting_bundle, refuting_bundle],
        )
        self.assertEqual(completed_overlap["missingConflicts"], [])

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
            supporting_head,
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
        current_supporting_bundle = self.root / "judgment-supporting-current"
        run_primary_judgment_bundle(
            self.root,
            "demo",
            judge,
            refuting_head,
            [supporting_head],
            current_supporting_bundle,
            transport=transport_for(supporting_head, "supports"),
        )
        _, supporting, supporting_run_digest = load_judgment_bundle(supporting_bundle)
        _, refuting, refuting_run_digest = load_judgment_bundle(refuting_bundle)
        self.assertNotEqual(supporting["judgmentId"], refuting["judgmentId"])
        self.assertEqual(
            [item["id"] for item in refuting["subjects"]], [refuting_head]
        )

        partial_projection = self.root / "targeted-partial-projection"
        supporting_partial = plan_primary_judgment_inputs(
            self.root,
            partial_projection,
            "demo",
            judge,
            refuting_head,
            [current_supporting_bundle],
            [supporting_head],
            target_subject_transaction_id=supporting_head,
        )
        self.assertEqual(
            [
                item["transactionId"]
                for item in supporting_partial["pendingTransactions"]
            ],
            [refuting_head],
        )
        refuting_partial = plan_primary_judgment_inputs(
            self.root,
            partial_projection,
            "demo",
            judge,
            refuting_head,
            [refuting_bundle],
            [refuting_head],
            target_subject_transaction_id=refuting_head,
        )
        self.assertEqual(
            [
                item["transactionId"]
                for item in refuting_partial["pendingTransactions"]
            ],
            [supporting_head],
        )
        with self.assertRaisesRegex(
            MathFlowError, "omit an attestation-ready subject"
        ):
            plan_primary_judgment_inputs(
                self.root,
                partial_projection,
                "demo",
                judge,
                refuting_head,
                [current_supporting_bundle],
                [supporting_head],
            )

        idempotent_projection = self.root / "targeted-idempotent-projection"
        publish_batch(idempotent_projection, [current_supporting_bundle])
        idempotent_target = plan_primary_judgment_inputs(
            self.root,
            idempotent_projection,
            "demo",
            judge,
            refuting_head,
            [current_supporting_bundle],
            [supporting_head],
            target_subject_transaction_id=supporting_head,
        )
        self.assertEqual(idempotent_target["newBundles"], [])
        self.assertEqual(
            [
                item["transactionId"]
                for item in idempotent_target["pendingTransactions"]
            ],
            [refuting_head],
        )

        reusable_projection = self.root / "reusable-projection"
        publish_batch(reusable_projection, [supporting_bundle])
        input_plan = plan_primary_judgment_inputs(
            self.root,
            reusable_projection,
            "demo",
            judge,
            refuting_head,
            [refuting_bundle],
            [refuting_head],
        )
        self.assertEqual(
            [item["judgmentId"] for item in input_plan["publishedBundles"]],
            [supporting["judgmentId"]],
        )
        self.assertEqual(
            [item["judgmentId"] for item in input_plan["newBundles"]],
            [refuting["judgmentId"]],
        )
        self.assertEqual(
            input_plan["coveredSubjectTransactionIds"],
            sorted([supporting_head, refuting_head]),
        )

        publish_batch(reusable_projection, [refuting_bundle])
        inherited_plan = plan_primary_judgment_inputs(
            self.root,
            reusable_projection,
            "demo",
            judge,
            refuting_head,
            [],
            [],
        )
        self.assertEqual(len(inherited_plan["publishedBundles"]), 2)
        self.assertEqual(inherited_plan["newBundles"], [])
        input_plan_path = self.root / "judgment-input-plan.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "judgment-input-plan",
                    "--problem",
                    "demo",
                    "--judge",
                    str(judge),
                    "--head",
                    refuting_head,
                    "--projection-dir",
                    str(reusable_projection),
                    "--output",
                    str(input_plan_path),
                ]
            ),
            0,
        )
        self.assertEqual(
            json.loads(input_plan_path.read_text(encoding="utf-8")), inherited_plan
        )

        conflicts = detect_conflicts([supporting_bundle, refuting_bundle])
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["claimKey"], "demo/main-claim")
        self.assertEqual(
            {item["stance"] for item in conflicts[0]["judgments"]},
            {"supports", "refutes"},
        )

        forged_conflict = copy.deepcopy(conflicts[0])
        forged_conflict["judgments"][0]["summary"] = "A forged routing summary."
        forged_core = {
            key: value for key, value in forged_conflict.items() if key != "conflictId"
        }
        forged_conflict["conflictId"] = f"sha256:{sha256_json(forged_core)}"
        with self.assertRaisesRegex(
            MathFlowError,
            "conflict does not match the supplied primary judgments",
        ):
            run_reconciliation_judgment_bundle(
                self.root,
                "demo",
                Path(__file__).parents[1]
                / "protocol/judges/openrouter-markdown-reconciliation-v1.json",
                refuting_head,
                forged_conflict,
                [supporting_bundle, refuting_bundle],
                self.root / "forged-reconciliation",
                transport=lambda _: self.fail(
                    "a forged conflict reached the reconciliation provider"
                ),
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

        alternate_reconciliation_responses = iter(
            [
                {
                    "id": "alternate-reconciliation-report",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": "# Alternate reconciliation\n\nA second assessment also leaves the conflict unresolved."
                            }
                        }
                    ],
                },
                {
                    "id": "alternate-reconciliation-extract",
                    "model": "openai/gpt-5.6-sol",
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "outcome": "unresolved",
                                        "summary": "The alternate assessment is not decisive.",
                                        "findings": [
                                            {
                                                "claimKey": "demo/main-claim",
                                                "stance": "uncertain",
                                                "summary": "The second conflict assessment remains open.",
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
        alternate_reconciliation_bundle = (
            self.root / "judgment-reconciliation-alternate"
        )
        run_reconciliation_judgment_bundle(
            self.root,
            "demo",
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-reconciliation-v1.json",
            refuting_head,
            conflicts[0],
            [supporting_bundle, refuting_bundle],
            alternate_reconciliation_bundle,
            transport=lambda _: next(alternate_reconciliation_responses),
        )
        (
            alternate_manifest,
            alternate_reconciliation,
            alternate_reconciliation_run_digest,
        ) = load_judgment_bundle(alternate_reconciliation_bundle)
        self.assertNotEqual(
            reconciliation["judgmentId"],
            alternate_reconciliation["judgmentId"],
        )

        atomic_reconciliation_projection = (
            self.root / "atomic-reconciliation-publication"
        )
        with self.assertRaisesRegex(
            MathFlowError, "multiple distinct reconciliation judgments"
        ):
            publish_batch(
                atomic_reconciliation_projection,
                [reconciliation_bundle, alternate_reconciliation_bundle],
            )
        self.assertFalse(atomic_reconciliation_projection.exists())

        reconciliation_identity_projection = (
            self.root / "reconciliation-identity-publication"
        )
        publish_batch(
            reconciliation_identity_projection,
            [supporting_bundle, refuting_bundle],
        )
        publish_batch(reconciliation_identity_projection, [reconciliation_bundle])
        with self.assertRaisesRegex(
            MathFlowError, "multiple distinct reconciliation judgments"
        ):
            publish_batch(
                reconciliation_identity_projection,
                [alternate_reconciliation_bundle],
            )
        identity_index_path = (
            reconciliation_identity_projection
            / "indexes/problems/demo/runs.json"
        )
        identity_index = json.loads(
            identity_index_path.read_text(encoding="utf-8")
        )
        self.assertEqual(len(identity_index), 3)

        alternate_hex = alternate_reconciliation_run_digest.removeprefix(
            "sha256:"
        )
        alternate_relative = (
            Path("objects")
            / "judgment"
            / alternate_hex[:2]
            / alternate_hex
        )
        shutil.copytree(
            alternate_reconciliation_bundle,
            reconciliation_identity_projection / alternate_relative,
        )
        identity_index.append(
            {
                "runDigest": alternate_reconciliation_run_digest,
                "runKind": "judgment",
                "problemId": alternate_manifest["problemId"],
                "path": alternate_relative.as_posix(),
            }
        )
        write(
            identity_index_path,
            json.dumps(identity_index, indent=2) + "\n",
        )

        reconciliation_judge = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-markdown-reconciliation-v1.json"
        )
        with self.assertRaisesRegex(
            MathFlowError,
            "multiple distinct reusable reconciliation judgments",
        ):
            plan_reconciliation_inputs(
                self.root,
                reconciliation_identity_projection,
                "demo",
                judge,
                reconciliation_judge,
                refuting_head,
                [supporting_bundle, refuting_bundle],
            )
        missing_reconciliation = plan_reconciliation_inputs(
            self.root,
            reusable_projection,
            "demo",
            judge,
            reconciliation_judge,
            refuting_head,
            [supporting_bundle, refuting_bundle],
        )
        self.assertEqual(
            [item["conflictId"] for item in missing_reconciliation["missingConflicts"]],
            [conflicts[0]["conflictId"]],
        )
        self.assertEqual(
            missing_reconciliation["matrix"],
            {
                "include": [
                    {
                        "ordinal": 1,
                        "conflictId": conflicts[0]["conflictId"],
                        "claimKey": "demo/main-claim",
                    }
                ]
            },
        )
        self.assertEqual(missing_reconciliation["publishedBundles"], [])
        complete_reconciliation = plan_reconciliation_inputs(
            self.root,
            reusable_projection,
            "demo",
            judge,
            reconciliation_judge,
            refuting_head,
            [supporting_bundle, refuting_bundle],
            [reconciliation_bundle],
            [conflicts[0]["conflictId"]],
        )
        self.assertEqual(complete_reconciliation["missingConflicts"], [])
        self.assertEqual(
            [item["judgmentId"] for item in complete_reconciliation["newBundles"]],
            [reconciliation["judgmentId"]],
        )
        publish_batch(reusable_projection, [reconciliation_bundle])
        inherited_reconciliation = plan_reconciliation_inputs(
            self.root,
            reusable_projection,
            "demo",
            judge,
            reconciliation_judge,
            refuting_head,
            [supporting_bundle, refuting_bundle],
        )
        self.assertEqual(inherited_reconciliation["missingConflicts"], [])
        self.assertEqual(len(inherited_reconciliation["publishedBundles"]), 1)
        reconciliation_plan_path = self.root / "reconciliation-plan.json"
        self.assertEqual(
            main(
                [
                    "--root",
                    str(self.root),
                    "reconciliation-plan",
                    "--problem",
                    "demo",
                    "--primary-judge",
                    str(judge),
                    "--reconciliation-judge",
                    str(reconciliation_judge),
                    "--head",
                    refuting_head,
                    "--projection-dir",
                    str(reusable_projection),
                    "--primary-judgment-dir",
                    str(supporting_bundle),
                    "--primary-judgment-dir",
                    str(refuting_bundle),
                    "--output",
                    str(reconciliation_plan_path),
                ]
            ),
            0,
        )
        self.assertEqual(
            json.loads(reconciliation_plan_path.read_text(encoding="utf-8")),
            inherited_reconciliation,
        )

        builder_path = (
            Path(__file__).parents[1]
            / "protocol/judges/openrouter-knowledge-builder-v1.json"
        )
        builder_digest = f"sha256:{sha256_json(load_judge_spec(builder_path))}"
        unsafe_scheduler = self.root / "coordination/unsafe-scheduler.json"
        unsafe_lane = record_completed_inputs(
            unsafe_scheduler,
            "demo",
            builder_digest,
            [supporting["judgmentId"], refuting["judgmentId"]],
            [],
            minimum_interval_seconds=0,
            now=90,
        )
        unsafe_claim = claim_due_build(
            unsafe_scheduler, unsafe_lane["laneId"], 90, 500
        )
        with self.assertRaisesRegex(
            MathFlowError, "opposed primary judgments without their conflict record"
        ):
            run_knowledge_build_bundle(
                self.root,
                "demo",
                builder_path,
                refuting_head,
                unsafe_claim,
                [supporting_bundle, refuting_bundle],
                None,
                self.root / "unsafe-knowledge-build",
                transport=lambda _: self.fail("formation called provider before conflict check"),
            )
        incomplete_scheduler = self.root / "coordination/incomplete-scheduler.json"
        with self.assertRaisesRegex(
            MathFlowError,
            "conflict dependency must name distinct primary judgments",
        ):
            record_completed_inputs(
                incomplete_scheduler,
                "demo",
                builder_digest,
                [supporting["judgmentId"]],
                [conflicts[0]["conflictId"]],
                minimum_interval_seconds=0,
                now=95,
                conflict_dependencies={
                    conflicts[0]["conflictId"]: [supporting["judgmentId"]]
                },
                reconciliation_dependencies={},
            )
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
            conflict_dependencies={
                conflicts[0]["conflictId"]: sorted(
                    [supporting["judgmentId"], refuting["judgmentId"]]
                )
            },
            reconciliation_dependencies={
                reconciliation["judgmentId"]: {
                    "conflictId": conflicts[0]["conflictId"],
                    "inputJudgmentIds": sorted(
                        [supporting["judgmentId"], refuting["judgmentId"]]
                    ),
                }
            },
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

        def trigger_with_dependencies(bundle_dirs: list[Path], now: int) -> None:
            arguments = [
                "--root",
                str(self.root),
                "knowledge-trigger",
                "--scheduler-file",
                str(scheduler),
                "--problem",
                "demo",
                "--builder-digest",
                scheduler_builder_digest,
                "--minimum-interval",
                "60",
                "--now",
                str(now),
                "--conflicts",
                str(conflicts_path),
                "--output",
                str(self.root / "knowledge-trigger.json"),
            ]
            for bundle_dir in bundle_dirs:
                arguments.extend(["--judgment-dir", str(bundle_dir)])
            self.assertEqual(main(arguments), 0)

        trigger_with_dependencies([supporting_bundle, refuting_bundle], 110)
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
            sorted([supporting["judgmentId"], refuting["judgmentId"]]),
        )
        self.assertEqual(second_build["conflictIds"], [conflicts[0]["conflictId"]])
        complete_build(
            scheduler,
            first_lane["laneId"],
            second_build["buildToken"],
            "sha256:" + "c" * 64,
            now=190,
        )
        trigger_with_dependencies(
            [supporting_bundle, refuting_bundle, reconciliation_bundle], 200
        )
        self.assertIsNone(claim_due_build(scheduler, first_lane["laneId"], 249, 500))
        third_build = claim_due_build(scheduler, first_lane["laneId"], 250, 500)
        self.assertEqual(
            third_build["judgmentIds"],
            sorted(
                [
                    supporting["judgmentId"],
                    refuting["judgmentId"],
                    reconciliation["judgmentId"],
                ]
            ),
        )
        self.assertEqual(third_build["conflictIds"], [conflicts[0]["conflictId"]])
        fail_build(
            scheduler,
            first_lane["laneId"],
            third_build["buildToken"],
            now=250,
        )
        self.assertIsNone(
            claim_due_build(scheduler, first_lane["laneId"], 549, 500)
        )
        retried_build = claim_due_build(scheduler, first_lane["laneId"], 550, 500)
        self.assertEqual(retried_build["buildToken"], third_build["buildToken"])
        complete_build(
            scheduler,
            first_lane["laneId"],
            retried_build["buildToken"],
            "sha256:" + "d" * 64,
            now=560,
        )
        trigger_with_dependencies(
            [supporting_bundle, refuting_bundle, reconciliation_bundle], 570
        )
        self.assertIsNone(claim_due_build(scheduler, first_lane["laneId"], 700, 500))

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
            canonical_ref=refuting_head,
        )
        self.assertEqual(catalog["repository"]["projectionRef"], "projections")
        self.assertEqual(catalog["defaultProjectionId"], formation_lane["laneId"])
        self.assertEqual(len(catalog["projections"]), 1)
        catalog_projection = catalog["projections"][0]
        self.assertEqual(catalog_projection["latestRunDigest"], knowledge_run_digest)
        self.assertEqual(catalog_projection["runCount"], 1)
        self.assertEqual(catalog_projection["data"]["problem"]["id"], "demo")
        self.assertEqual(len(catalog_projection["data"]["judgments"]), 3)

        write(
            self.root / "protocol/problem-registry.json",
            json.dumps(
                {
                    "schemaVersion": 1,
                    "archivedProblems": ["demo"],
                }
            )
            + "\n",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "Archive demo")
        archived_head = git(self.root, "rev-parse", "HEAD")
        archived_catalog = export_viewer_catalog(
            self.root,
            projection,
            "example/math-flow",
            canonical_ref=archived_head,
        )
        self.assertEqual(archived_catalog["projections"], [])
        self.assertIsNone(archived_catalog["defaultProjectionId"])

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
