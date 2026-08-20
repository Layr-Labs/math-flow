from __future__ import annotations

import json
import unittest
from pathlib import Path

from math_flow.judges import load_judge_spec


class ResearchProgramProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]

    def test_v3_builder_uses_revisable_taxonomy_policy(self) -> None:
        builder_path = (
            self.root
            / "protocol/judges/openrouter-research-program-builder-v3.json"
        )
        builder = load_judge_spec(builder_path)

        self.assertEqual(builder["implementation"], "openrouter-knowledge-builder-v3")
        self.assertEqual(
            builder["outputProfile"], "math-flow/knowledge-build-markdown-v2"
        )
        self.assertEqual(
            builder["outputAdapter"],
            "select-form-extract-knowledge-revisions-v2",
        )
        self.assertEqual(builder["reducer"], "hierarchical-knowledge-revisions-v3")
        self.assertIn("do not treat the current taxonomy as immutable", builder["systemPrompt"])
        self.assertIn("split a broad program into sibling successors", builder["systemPrompt"])
        self.assertIn("central exact-value question", builder["systemPrompt"])
        self.assertIn("never itself a knowledge node", builder["systemPrompt"])

    def test_v2_builder_remains_frozen_for_active_projection_replay(self) -> None:
        builder = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-research-program-builder-v2.json"
        )
        self.assertEqual(builder["implementation"], "openrouter-knowledge-builder-v2")
        self.assertIn("additive institutional memory", builder["systemPrompt"])
        self.assertNotIn("split a broad program", builder["systemPrompt"])

    def test_specialized_projection_has_distinct_scope_and_shared_judges(self) -> None:
        default = json.loads(
            (self.root / "protocol/projections/openrouter-research-v1.json").read_text(
                encoding="utf-8"
            )
        )
        specialized = json.loads(
            (
                self.root
                / "protocol/projections/openrouter-no-three-in-line-research-programs-v2.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(default["allowedProblems"], ["*"])
        self.assertEqual(specialized["allowedProblems"], ["no-three-in-line-77"])
        self.assertNotEqual(default["id"], specialized["id"])
        if default["primaryJudge"] == (
            "protocol/judges/openrouter-validity-judgment-v2.json"
        ):
            self.assertIsNone(default["reconciliationJudge"])
            self.assertEqual(
                default["knowledgeBuilder"],
                "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
            )
        else:
            self.assertEqual(
                default["primaryJudge"],
                "protocol/judges/openrouter-markdown-judgment-v1.json",
            )
            self.assertEqual(
                default["reconciliationJudge"],
                "protocol/judges/openrouter-markdown-reconciliation-v1.json",
            )
            self.assertEqual(
                default["knowledgeBuilder"],
                "protocol/judges/openrouter-research-program-builder-v2.json",
            )
        if default["primaryJudge"].endswith("validity-judgment-v2.json"):
            self.assertNotEqual(default["primaryJudge"], specialized["primaryJudge"])
        else:
            self.assertEqual(default["primaryJudge"], specialized["primaryJudge"])
        self.assertIsNotNone(specialized["reconciliationJudge"])
        self.assertEqual(
            specialized["knowledgeBuilder"],
            "protocol/judges/openrouter-research-program-builder-v2.json",
        )

    def test_hierarchical_research_builder_separates_state_from_credit(self) -> None:
        builder = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-hierarchical-research-builder-v2.json"
        )
        self.assertEqual(
            builder["implementation"],
            "openrouter-hierarchical-research-builder-v2",
        )
        self.assertEqual(builder["outputProfile"], "math-flow/hierarchical-research-v2")
        self.assertEqual(builder["reducer"], "batched-research-state-v2")
        self.assertNotIn("credit", builder["stages"])
        self.assertIn("exclude invalid and indeterminate claims", builder["systemPrompt"])

    def test_validity_v3_components_are_additive_and_self_contextual(self) -> None:
        judge = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-validity-judgment-v3.json"
        )
        builder = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-hierarchical-research-builder-v3.json"
        )
        self.assertEqual(judge["contextProjection"], "openrouter-research-v2")
        self.assertEqual(judge["inputBuilder"], "claim-evidence-packet-v3")
        self.assertIn("terminal objective attestation", judge["description"])
        self.assertEqual(
            builder["inputBuilder"],
            "accepted-validity-batch-program-state-v3",
        )
        self.assertIn("reference", builder["rubric"]["dependencyBoundary"])
        self.assertIn(
            "independent unjudged assertion",
            builder["rubric"]["atomicClaimBoundary"],
        )
        self.assertIn("unclaimed content has not passed", builder["systemPrompt"])

    def test_validity_v4_components_bind_reference_attestations_additively(self) -> None:
        judge = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-validity-judgment-v4.json"
        )
        builder = load_judge_spec(
            self.root
            / "protocol/judges/openrouter-hierarchical-research-builder-v4.json"
        )
        self.assertEqual(judge["contextProjection"], "openrouter-research-v3")
        self.assertEqual(judge["inputBuilder"], "claim-evidence-packet-v4")
        self.assertEqual(judge["outputProfile"], "math-flow/validity-judgment-v4")
        self.assertIn("subject and declared references", judge["description"])
        self.assertIn("supplied attestations", judge["systemPrompt"])
        self.assertEqual(
            builder["inputBuilder"],
            "accepted-validity-batch-program-state-v4",
        )
        self.assertEqual(
            builder["outputProfile"], "math-flow/hierarchical-research-v4"
        )
        self.assertIn(
            "independent unjudged assertion",
            builder["rubric"]["atomicClaimBoundary"],
        )
        self.assertIn("unclaimed content has not passed", builder["systemPrompt"])
        self.assertIn("do not reinterpret", builder["systemPrompt"])

    def test_attestation_publication_redispatches_v3_and_v4_validity_streams(self) -> None:
        attestation = (
            self.root / ".github/workflows/project-attestation.yml"
        ).read_text(encoding="utf-8")
        projection = (
            self.root / ".github/workflows/project-openrouter.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("actions: write", attestation)
        self.assertIn("validity-judgment-v3.json", attestation)
        self.assertIn("validity-judgment-v4.json", attestation)
        self.assertIn("group_by(.judgmentStreamId)", attestation)
        self.assertIn("project-openrouter.yml", attestation)
        self.assertIn("attestation-coverage-before-", attestation)
        self.assertIn("attestation-coverage-after-", attestation)
        self.assertIn("index($id)", attestation)
        self.assertIn('-f subject_transaction="$subject_transaction"', attestation)
        self.assertIn("openrouter-validity-judgment-v3", projection)
        self.assertIn("openrouter-validity-judgment-v4", projection)
        self.assertIn("deferredTransactions", projection)

    def test_scheduled_research_v3_wakeup_targets_only_authorized_ready_subjects(self) -> None:
        wakeup = (
            self.root / ".github/workflows/projection-wakeup.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("projection-wakeup-plan", wakeup)
        self.assertIn("--targeted-projection openrouter-research-v3", wakeup)
        self.assertIn("--targeted-problem bssc-sum-capacity", wakeup)
        self.assertIn("--targeted-problem no-three-in-line-77", wakeup)
        self.assertIn(".subjectTransactionId // empty", wakeup)
        self.assertIn(
            'if [[ -n "$subject_transaction" ]]; then', wakeup
        )
        self.assertIn(
            'command+=(-f subject_transaction="$subject_transaction")', wakeup
        )
        self.assertIn(".requireNoPrimaryWork", wakeup)
        self.assertIn(
            'command+=(-f require_no_primary_work=true)', wakeup
        )
        self.assertIn(".dispatches[]", wakeup)

    def test_hosted_primary_judgments_serialize_only_the_same_subject(self) -> None:
        workflow = (
            self.root / ".github/workflows/project-openrouter.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("\nconcurrency:\n", workflow)
        self.assertIn(
            "inputs.projection }}-${{ inputs.problem }}-${{ "
            "inputs.subject_transaction || 'batch'",
            workflow,
        )
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("--subject-transaction", workflow)
        self.assertIn("require_no_primary_work:", workflow)
        self.assertIn(
            "Formation-only wake found live missing primary work", workflow
        )
        self.assertIn(
            '-f require_no_primary_work="$MATH_FLOW_REQUIRE_NO_PRIMARY_WORK"',
            workflow,
        )
        self.assertIn(
            '-f subject_transaction="$MATH_FLOW_SUBJECT_TRANSACTION"', workflow
        )
        self.assertIn("reconciliation_enabled", workflow)
        self.assertIn("This projection has no reconciliation stage.", workflow)
        self.assertEqual(
            workflow.count("uses: actions/checkout@"),
            workflow.count('ref: "${{ github.sha }}"'),
        )
        self.assertNotIn("ref: main", workflow)
        self.assertEqual(
            workflow.count("--canonical-ref refs/remotes/origin/main"), 3
        )
        self.assertGreaterEqual(
            workflow.count(
                "+refs/heads/main:refs/remotes/origin/main"
            ),
            3,
        )
        self.assertLess(
            workflow.index("\n  publish_primary:\n"),
            workflow.index("\n  reconciliation_plan:\n"),
        )
        self.assertLess(
            workflow.index("\n  publish_reconciliation:\n"),
            workflow.index("\n  form:\n"),
        )
        self.assertNotIn("\n  publish:\n", workflow)
        form = workflow.split("\n  form:\n", 1)[1].split(
            "\n  dispatch-next:\n", 1
        )[0]
        self.assertIn(
            'group: "openrouter-formation-${{ inputs.projection }}-${{ inputs.problem }}"',
            form,
        )
        self.assertIn("cancel-in-progress: false", form)
        self.assertIn("github-publish-projection", form)
        self.assertIn(
            "if: always() && steps.staging.outputs.changed == 'true'",
            form,
        )
        self.assertIn(
            "if: always() && steps.claim.outcome == 'success'",
            form,
        )
        self.assertIn("python -m math_flow knowledge-fail", form)
        self.assertIn("pendingTransactions", form)
        self.assertIn("reconciliation_enabled", form)
        primary_publication = workflow.split(
            "\n  publish_primary:\n", 1
        )[1].split("\n  reconciliation_plan:\n", 1)[0]
        self.assertNotIn("scheduler.json", primary_publication)
        self.assertNotIn("knowledge-trigger", primary_publication)
        self.assertIn(
            "inputs.subject_transaction == '' && needs.judgment.result == 'failure'",
            primary_publication,
        )
        self.assertIn("--allow-expected-subset", primary_publication)
        self.assertIn("--retain-expected-subset", primary_publication)
        self.assertIn("-n \"$MATH_FLOW_RESUME_RUN_ID\"", primary_publication)
        self.assertIn("Published the retained primary subset", primary_publication)
        self.assertLess(
            primary_publication.index('publish_one "$bundle_dir"'),
            primary_publication.index("Published the retained primary subset"),
        )
        reconciliation_publication = workflow.split(
            "\n  publish_reconciliation:\n", 1
        )[1].split("\n  form:\n", 1)[0]
        self.assertIn(
            "needs.reconciliation.result == 'failure'",
            reconciliation_publication,
        )
        self.assertIn("--allow-expected-subset", reconciliation_publication)
        self.assertIn(
            "Published the successful reconciliation subset",
            reconciliation_publication,
        )
        self.assertLess(
            reconciliation_publication.index('publish_one "$bundle_dir"'),
            reconciliation_publication.index(
                "Published the successful reconciliation subset"
            ),
        )


if __name__ == "__main__":
    unittest.main()
