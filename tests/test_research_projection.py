from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.cli import main
from math_flow.artifacts import load_manifest, read_verified_artifact
from math_flow.coordination import (
    claim_due_build,
    complete_build,
    publish_batch,
    record_completed_inputs,
)
from math_flow.credit import run_credit_assignment_bundle
from math_flow.credit_context import build_credit_context
from math_flow.judgments import load_judgment_bundle, run_primary_judgment_bundle
from math_flow.errors import MathFlowError
from math_flow.judges import load_judge_spec, load_source
from math_flow.governance import resolve_projection
from math_flow.repository import sha256_json
from math_flow.research_credit import (
    load_hierarchical_credit_assignment_bundle,
)
from math_flow.research_state import empty_research_program_state
from math_flow.research_projection import (
    load_research_build_bundle,
    load_research_credit_refresh_bundle,
    load_research_update_bundle,
    replay_research_protocol,
    run_research_build_bundle,
    run_research_credit_refresh_bundle,
    run_research_update_bundle,
)
from math_flow.validity import research_state_dependency_context
from math_flow.viewer import export_viewer_catalog, export_viewer_data


ROOT = Path(__file__).resolve().parents[1]
PROBLEM = "bssc-sum-capacity"
TX = "d638c346212db3e75f6a53dcebcfd09f55125852"
TRANSACTIONS = [
    TX,
    "7e7626cbff7270572d51a8fda719154ab602907f",
    "c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6",
    "f236017c62c67ce4218c1f81ea34134f0954b556",
]


def response(content: str, index: int) -> dict[str, object]:
    return {
        "id": f"response-{index}",
        "model": "openai/gpt-5.6-sol",
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        "choices": [
            {"finish_reason": "stop", "message": {"content": content}}
        ],
    }


def accepted_replay_response(
    request: dict[str, object],
    index: int,
    transaction_id: str = TX,
    credit_transaction_ids: list[str] | None = None,
) -> dict[str, object]:
    schema = request.get("response_format", {}).get("json_schema", {}).get("schema")
    if schema is None:
        return response(
            "# Rigorous audit\n\nEvery declared obligation is established in this fixture.",
            index,
        )
    schema_stack = [schema]
    while schema_stack:
        node = schema_stack.pop()
        if isinstance(node, dict):
            if "oneOf" in node:
                raise AssertionError("strict output schemas must not use oneOf")
            if "uniqueItems" in node:
                raise AssertionError(
                    "strict output schemas must leave uniqueness to the reducer"
                )
            if "const" in node and "type" not in node:
                raise AssertionError("strict-schema constants must declare their JSON type")
            schema_stack.extend(node.values())
        elif isinstance(node, list):
            schema_stack.extend(node)
    properties = schema["properties"]
    if "assessments" in properties:
        claim_keys = properties["assessments"]["items"]["properties"]["claimKey"][
            "enum"
        ]
        value = {
            "assessments": [
                {
                    "claimKey": claim_key,
                    "status": "valid",
                    "premiseStatus": "not-required",
                    "summary": "The fixture accepts the exact declared claim.",
                    "scopeQualifications": [],
                    "evidenceIssues": [],
                    "evidenceTransactionIds": [],
                }
                for claim_key in claim_keys
            ]
        }
    elif "contribution" in properties:
        operation_schema = properties["operations"]["items"]
        if "anyOf" not in operation_schema or "oneOf" in operation_schema:
            raise AssertionError(
                "organizer operations must use OpenAI-supported nested anyOf"
            )
        claim_keys = properties["contribution"]["properties"]["claimKeys"]["items"][
            "enum"
        ]
        suffix = transaction_id[:12]
        value = {
            "schemaVersion": 1,
            "operations": [
                {
                    "entityKind": "thread",
                    "entityId": f"root/fixture-line-{suffix}",
                    "baseDigest": None,
                    "value": {
                        "id": f"root/fixture-line-{suffix}",
                        "programId": "root",
                        "title": "Fixture research line",
                        "summary": "Track the accepted fixture result.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "2",
                        "conditions": [],
                        "sourceTransactionIds": [transaction_id],
                    },
                },
                {
                    "entityKind": "item",
                    "entityId": f"root/fixture-result-{suffix}",
                    "baseDigest": None,
                    "value": {
                        "id": f"root/fixture-result-{suffix}",
                        "programId": "root",
                        "type": "result",
                        "title": "Accepted fixture result",
                        "summary": "Represent every accepted claim in one durable result.",
                        "claimRefs": [
                            {
                                "transactionId": transaction_id,
                                "claimKey": claim_key,
                            }
                            for claim_key in claim_keys
                        ],
                        "sourceTransactionIds": [transaction_id],
                        "dependencyItemIds": [],
                    },
                },
            ],
            "contribution": {
                "claimKeys": claim_keys,
                "directProgramId": "root",
                "directThreadIds": [f"root/fixture-line-{suffix}"],
                "itemIds": [f"root/fixture-result-{suffix}"],
            },
        }
    else:
        credit_ids = credit_transaction_ids or [transaction_id]
        value = {
            "schemaVersion": 1,
            "evaluations": [
                {
                    "programId": "root",
                    "unattributedWork": "0",
                    "rationale": "The fixture assigns all local causal work.",
                    "children": [
                        {
                            "kind": "contribution",
                            "id": credit_id,
                            "counterfactual": "Remove the accepted fixture result.",
                            "directEffects": [
                                {
                                    "threadId": f"root/fixture-line-{credit_id[:12]}",
                                    "withoutWork": "3",
                                    "withWork": "1",
                                    "rationale": "The result saves two units on its line.",
                                }
                            ],
                            "obviatedEffects": [],
                            "confidence": "medium",
                            "evidenceRefs": [credit_id],
                        }
                        for credit_id in credit_ids
                    ],
                }
            ],
        }
    return response(json.dumps(value), index)


class ResearchProjectionTests(unittest.TestCase):
    def _validity_bundle(
        self,
        directory: Path,
        transaction_id: str,
        *,
        status: str = "valid",
        repository: Path = ROOT,
    ) -> Path:
        calls = 0

        def fake_transport(request: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            schema = (
                request.get("response_format", {})
                .get("json_schema", {})
                .get("schema")
            )
            if schema is None:
                return response("# Audit\n\nFixture validity audit.", calls)
            claim_keys = schema["properties"]["assessments"]["items"][
                "properties"
            ]["claimKey"]["enum"]
            return response(
                json.dumps(
                    {
                        "assessments": [
                            {
                                "claimKey": key,
                                "status": status,
                                "premiseStatus": "not-required",
                                "summary": f"Fixture assessment: {status}.",
                                "scopeQualifications": [],
                                "evidenceIssues": (
                                    [] if status == "valid" else ["Fixture defect."]
                                ),
                                "evidenceTransactionIds": [],
                            }
                            for key in claim_keys
                        ]
                    }
                ),
                calls,
            )

        output = directory / f"validity-{transaction_id[:12]}"
        run_primary_judgment_bundle(
            repository,
            PROBLEM,
            repository / "protocol/judges/openrouter-validity-judgment-v2.json",
            transaction_id,
            [transaction_id],
            output,
            projection_root=None,
            transport=fake_transport,
        )
        return output

    @staticmethod
    def _batch_transport(request: dict[str, object]) -> dict[str, object]:
        schema = request["response_format"]["json_schema"]["schema"]
        properties = schema["properties"]
        variants = properties["contributions"]["items"]["anyOf"]
        operations: list[dict[str, object]] = []
        contributions: list[dict[str, object]] = []
        for variant in variants:
            contribution_properties = variant["properties"]
            transaction_id = contribution_properties["transactionId"]["const"]
            claim_keys = contribution_properties["claimKeys"]["items"]["enum"]
            suffix = transaction_id[:12]
            thread_id = f"root/batch-line-{suffix}"
            item_id = f"root/batch-result-{suffix}"
            operations.extend(
                [
                    {
                        "entityKind": "thread",
                        "entityId": thread_id,
                        "baseDigest": None,
                        "value": {
                            "id": thread_id,
                            "programId": "root",
                            "title": f"Batch line {suffix}",
                            "summary": "Track one accepted batch contribution.",
                            "kind": "research",
                            "status": "active",
                            "expectedExposure": "1",
                            "conditions": [],
                            "sourceTransactionIds": [transaction_id],
                        },
                    },
                    {
                        "entityKind": "item",
                        "entityId": item_id,
                        "baseDigest": None,
                        "value": {
                            "id": item_id,
                            "programId": "root",
                            "type": "result",
                            "title": f"Batch result {suffix}",
                            "summary": "Represent the exact accepted claims.",
                            "claimRefs": [
                                {"transactionId": transaction_id, "claimKey": key}
                                for key in claim_keys
                            ],
                            "sourceTransactionIds": [transaction_id],
                            "dependencyItemIds": [],
                        },
                    },
                ]
            )
            contributions.append(
                {
                    "transactionId": transaction_id,
                    "claimKeys": claim_keys,
                    "directProgramId": "root",
                    "directThreadIds": [thread_id],
                    "itemIds": [item_id],
                }
            )
        return response(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "operations": operations,
                    "contributions": contributions,
                }
            ),
            1,
        )

    def _build_claim(
        self, directory: Path, validity_dirs: list[Path]
    ) -> dict[str, object]:
        builder = load_judge_spec(
            ROOT
            / "protocol/judges/openrouter-hierarchical-research-builder-v2.json"
        )
        judgment_ids = []
        for validity_dir in validity_dirs:
            _, judgment, _ = load_judgment_bundle(validity_dir)
            judgment_ids.append(str(judgment["judgmentId"]))
        scheduler = directory / "scheduler.json"
        lane = record_completed_inputs(
            scheduler,
            PROBLEM,
            f"sha256:{sha256_json(builder)}",
            judgment_ids,
            [],
            0,
            1,
        )
        claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
        assert claim is not None
        return claim

    def test_batched_research_build_is_independent_of_bundle_completion_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validity_dirs = [
                self._validity_bundle(root, transaction_id)
                for transaction_id in TRANSACTIONS[:2]
            ]
            claim = self._build_claim(root, validity_dirs)
            states = []
            for index, ordered_dirs in enumerate(
                [validity_dirs, list(reversed(validity_dirs))]
            ):
                output = root / f"research-build-{index}"
                run_research_build_bundle(
                    ROOT,
                    PROBLEM,
                    ROOT
                    / "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
                    TRANSACTIONS[1],
                    claim,
                    ordered_dirs,
                    None,
                    output,
                    transport=self._batch_transport,
                )
                manifest, state, _ = load_research_build_bundle(output)
                self.assertEqual(manifest["runKind"], "knowledge-build")
                states.append(state)
            self.assertEqual(states[0], states[1])
            self.assertEqual(set(states[0]["contributions"]), set(TRANSACTIONS[:2]))
            later_source = load_source(ROOT, PROBLEM, TRANSACTIONS[2])
            context = research_state_dependency_context(
                root / "research-build-0",
                PROBLEM,
                later_source,
                3,
                [TRANSACTIONS[0]],
            )
            self.assertEqual(context["sourceKind"], "research-program-state")
            self.assertEqual(context["unresolvedDependencyTransactionIds"], [])
            viewer = export_viewer_data(
                ROOT,
                PROBLEM,
                TRANSACTIONS[1],
                [root / "research-build-0"],
                judgment_dirs=validity_dirs,
            )
            viewer_nodes = viewer["runs"][0]["state"]["nodes"]
            self.assertIn("root", viewer_nodes)
            self.assertTrue(
                any(node_id.startswith("item:") for node_id in viewer_nodes)
            )

    def test_invalid_judgment_is_processed_but_excluded_from_research_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = self._validity_bundle(root, TRANSACTIONS[0])
            invalid = self._validity_bundle(
                root, TRANSACTIONS[1], status="invalid"
            )
            claim = self._build_claim(root, [valid, invalid])
            output = root / "research-build"
            run_research_build_bundle(
                ROOT,
                PROBLEM,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
                "HEAD",
                claim,
                [invalid, valid],
                None,
                output,
                transport=self._batch_transport,
            )
            _, state, _ = load_research_build_bundle(output)
            self.assertEqual(set(state["contributions"]), {TRANSACTIONS[0]})

    def test_all_invalid_batch_advances_scheduler_without_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self._validity_bundle(
                root, TRANSACTIONS[0], status="indeterminate"
            )
            claim = self._build_claim(root, [invalid])

            def unexpected(_: dict[str, object]) -> dict[str, object]:
                raise AssertionError("excluded judgments must not invoke the organizer")

            output = root / "research-build"
            manifest = run_research_build_bundle(
                ROOT,
                PROBLEM,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
                "HEAD",
                claim,
                [invalid],
                None,
                output,
                transport=unexpected,
            )
            _, state, _ = load_research_build_bundle(output)
            self.assertEqual(state["contributions"], {})
            self.assertEqual(manifest["providerRuns"], [])

    def test_hierarchical_credit_uses_common_horizon_and_batched_historical_base(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            subprocess.run(
                ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(repository)],
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Research Credit Test"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "credit-test@example.com"],
                cwd=repository,
                check=True,
            )
            research_projection_path = (
                repository / "protocol/projections/openrouter-research-v1.json"
            )
            research_projection_path.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "id": "openrouter-research-v1",
                        "description": "Fixture batched hierarchical research projection.",
                        "status": "active",
                        "engine": "openrouter-repository-v1",
                        "allowedProblems": ["*"],
                        "primaryJudge": "protocol/judges/openrouter-validity-judgment-v2.json",
                        "reconciliationJudge": None,
                        "knowledgeBuilder": "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
                        "scheduling": {
                            "judgmentMaxParallel": 16,
                            "knowledgeMinimumIntervalSeconds": 300,
                            "maximumJudgmentsPerBuild": 500,
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            projection_path = (
                repository
                / "protocol/projections/openrouter-research-credit-v2.json"
            )
            projection_path.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "id": "openrouter-research-credit-v2",
                        "description": "Fixture common-horizon hierarchical credit overlay.",
                        "status": "active",
                        "engine": "overlay-repository-v1",
                        "allowedProblems": ["*"],
                        "runner": {
                            "implementation": "openrouter-hierarchical-research-credit-v2",
                            "spec": "protocol/judges/openrouter-hierarchical-research-credit-v2.json",
                        },
                        "dependencies": [
                            {
                                "name": "research",
                                "projectionId": "openrouter-research-v1",
                                "artifactRole": "research-program-state",
                            }
                        ],
                        "scheduling": {"minimumIntervalSeconds": 3600},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    "git",
                    "add",
                    "protocol/projections/openrouter-research-v1.json",
                    "protocol/projections/openrouter-research-credit-v2.json",
                ],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-qm", "Add fixture credit projection"],
                cwd=repository,
                check=True,
            )
            projection_root = root / "published"
            validity_dirs = [
                self._validity_bundle(
                    root, transaction_id, repository=repository
                )
                for transaction_id in TRANSACTIONS[:2]
            ]
            invalid = self._validity_bundle(
                root,
                TRANSACTIONS[2],
                status="invalid",
                repository=repository,
            )
            all_judgments = [*validity_dirs, invalid]
            builder = load_judge_spec(
                repository
                / "protocol/judges/openrouter-hierarchical-research-builder-v2.json"
            )
            builder_digest = f"sha256:{sha256_json(builder)}"
            producer = resolve_projection(
                repository, "openrouter-research-v1", PROBLEM, "HEAD"
            )
            judgment_ids = [
                str(load_judgment_bundle(bundle)[1]["judgmentId"])
                for bundle in all_judgments
            ]
            scheduler = projection_root / "coordination" / "scheduler.json"
            lane = record_completed_inputs(
                scheduler,
                PROBLEM,
                builder_digest,
                judgment_ids,
                [],
                300,
                1,
                projection_spec_digest=str(producer["projectionSpecDigest"]),
            )
            claim = claim_due_build(
                scheduler, str(lane["laneId"]), 1, 500
            )
            assert claim is not None
            build = root / "research-build"
            run_research_build_bundle(
                repository,
                PROBLEM,
                repository
                / "protocol/judges/openrouter-hierarchical-research-builder-v2.json",
                "HEAD",
                claim,
                list(reversed(all_judgments)),
                None,
                build,
                transport=self._batch_transport,
            )
            _, build_digest = load_manifest(build)
            publish_batch(projection_root, [*all_judgments, build])
            complete_build(
                scheduler,
                str(lane["laneId"]),
                str(claim["buildToken"]),
                build_digest,
                2,
            )

            calls: list[dict[str, object]] = []

            def credit_transport(request: dict[str, object]) -> dict[str, object]:
                calls.append(request)
                schema = request["response_format"]["json_schema"]["schema"]
                program_ids = schema["properties"]["evaluations"]["items"][
                    "properties"
                ]["programId"]["enum"]
                self.assertEqual(program_ids, ["root"])
                children = []
                for transaction_id in TRANSACTIONS[:2]:
                    children.append(
                        {
                            "kind": "contribution",
                            "id": transaction_id,
                            "counterfactual": "Remove this accepted result while retaining independent information.",
                            "directEffects": [
                                {
                                    "threadId": f"root/batch-line-{transaction_id[:12]}",
                                    "withoutWork": "3",
                                    "withWork": "1",
                                    "rationale": "Two units of direct local work are avoided.",
                                }
                            ],
                            "obviatedEffects": [
                                {
                                    "threadId": "root/unstructured-search",
                                    "withoutWork": "2",
                                    "withWork": "1.5",
                                    "rationale": "The result narrows pre-existing unstructured search.",
                                }
                            ],
                            "confidence": "medium",
                            "evidenceRefs": [transaction_id],
                        }
                    )
                return response(
                    json.dumps(
                        {
                            "schemaVersion": 1,
                            "evaluations": [
                                {
                                    "programId": "root",
                                    "unattributedWork": "1",
                                    "rationale": "One unit remains unattributed.",
                                    "children": children,
                                }
                            ],
                        }
                    ),
                    1,
                )

            output = root / "credit"
            run_credit_assignment_bundle(
                repository,
                projection_root,
                "openrouter-research-credit-v2",
                PROBLEM,
                "HEAD",
                output,
                transport=credit_transport,
                as_of=3,
            )
            manifest, credit_state, _ = load_hierarchical_credit_assignment_bundle(
                output
            )
            self.assertEqual(len(calls), 1)
            self.assertEqual(manifest["runKind"], "credit-assignment")
            self.assertEqual(
                set(credit_state["allocations"]), set(TRANSACTIONS[:2])
            )
            children = credit_state["evaluations"]["root"]["children"]
            empty_digest = empty_research_program_state(PROBLEM)["stateDigest"]
            self.assertEqual(
                {child["referenceBaseStateDigest"] for child in children},
                {empty_digest},
            )
            self.assertEqual(
                len({child["referencePostStateDigest"] for child in children}),
                1,
            )
            self.assertTrue(all(child["totalWork"] == "2.5" for child in children))
            history = json.loads(
                read_verified_artifact(
                    output, manifest, "research-history-trace"
                )
            )
            accepted = history[0]["acceptedRecords"]
            self.assertEqual(
                {record["subjectTransactionId"] for record in accepted},
                set(TRANSACTIONS[:2]),
            )
            evidence = read_verified_artifact(
                output, manifest, "accepted-submission-evidence"
            ).decode("utf-8")
            self.assertNotIn(TRANSACTIONS[2], evidence)
            prompt = calls[0]["messages"][1]["content"]
            self.assertIn("Original accepted submissions", prompt)
            self.assertIn("historical local reference contexts", prompt)
            publish_batch(projection_root, [output])
            source = load_source(repository, PROBLEM, "HEAD")
            credit_context, report = build_credit_context(
                repository,
                projection_root,
                PROBLEM,
                "HEAD",
                list(source["transactions"]),
                credit_projection_id="openrouter-research-credit-v2",
            )
            self.assertEqual(credit_context["status"], "current")
            self.assertEqual(
                credit_context["semantics"]["kind"],
                "hierarchical-two-term-causal-work",
            )
            self.assertEqual(
                set(credit_context["hierarchicalCredit"]["allocations"]),
                set(TRANSACTIONS[:2]),
            )
            self.assertIsNone(report)
            catalog = export_viewer_catalog(
                repository,
                projection_root,
                "Layr-Labs/math-flow",
                canonical_ref="HEAD",
                projection_ref="projections",
            )
            hierarchical = catalog["hierarchicalCreditProjections"]
            selected = next(
                item
                for item in hierarchical
                if item["problemId"] == PROBLEM
                and item["label"] == "openrouter-research-credit-v2"
            )
            self.assertEqual(selected["selectionStatus"], "current")
            self.assertEqual(selected["runCount"], 1)
            self.assertEqual(
                set(selected["runs"][0]["creditState"]["allocations"]),
                set(TRANSACTIONS[:2]),
            )

    def test_knowledge_trigger_derives_submission_dependencies_from_validity_packets(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dependency = self._validity_bundle(root, TRANSACTIONS[2])
            dependent = self._validity_bundle(root, TRANSACTIONS[3])
            scheduler = root / "scheduler.json"
            output = root / "lane.json"
            status = main(
                [
                    "--root",
                    str(ROOT),
                    "knowledge-trigger",
                    "--scheduler-file",
                    str(scheduler),
                    "--problem",
                    PROBLEM,
                    "--head",
                    TRANSACTIONS[3],
                    "--builder",
                    str(
                        ROOT
                        / "protocol/judges/openrouter-hierarchical-research-builder-v2.json"
                    ),
                    "--minimum-interval",
                    "0",
                    "--judgment-dir",
                    str(dependent),
                    "--judgment-dir",
                    str(dependency),
                    "--now",
                    "1",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(status, 0)
            _, dependency_judgment, _ = load_judgment_bundle(dependency)
            _, dependent_judgment, _ = load_judgment_bundle(dependent)
            lane = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                lane["judgmentDependencies"][dependent_judgment["judgmentId"]],
                [dependency_judgment["judgmentId"]],
            )

    def test_full_bssc_fixture_replay_uses_seventeen_calls(self) -> None:
        calls = 0

        def fake_transport(request: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            if calls == 17:
                return accepted_replay_response(
                    request,
                    calls,
                    TRANSACTIONS[-1],
                    credit_transaction_ids=TRANSACTIONS,
                )
            transaction_id = TRANSACTIONS[(calls - 1) // 4]
            return accepted_replay_response(request, calls, transaction_id)

        with tempfile.TemporaryDirectory() as directory:
            summary = replay_research_protocol(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                Path(directory) / "replay",
                transport=fake_transport,
            )

        self.assertEqual(calls, 17)
        self.assertEqual(summary["contributionCount"], 4)
        self.assertEqual(summary["acceptedContributionCount"], 4)
        self.assertEqual(summary["providerCallCount"], 17)
        self.assertEqual(summary["providerCallsPerformed"], 17)
        self.assertEqual(summary["providerCallsReusedFromCheckpoint"], 0)
        self.assertEqual(summary["providerCallsCoveredByReusedBundles"], 0)

    def test_replay_resumes_bundles_and_request_checkpoints(self) -> None:
        first_calls = 0

        def failing_transport(request: dict[str, object]) -> dict[str, object]:
            nonlocal first_calls
            first_calls += 1
            if first_calls == 4:
                return response(
                    json.dumps({"schemaVersion": 1, "evaluations": []}),
                    first_calls,
                )
            return accepted_replay_response(request, first_calls)

        resumed_calls = 0

        def resumed_transport(request: dict[str, object]) -> dict[str, object]:
            nonlocal resumed_calls
            resumed_calls += 1
            return accepted_replay_response(request, resumed_calls + 10)

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "replay"
            with self.assertRaises(MathFlowError):
                replay_research_protocol(
                    ROOT,
                    PROBLEM,
                    ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                    ROOT
                    / "protocol/judges/openrouter-hierarchical-research-v1.json",
                    output_dir,
                    head=TX,
                    transport=failing_transport,
                )
            self.assertEqual(first_calls, 4)
            self.assertEqual(len(list((output_dir / "checkpoints").glob("*.json"))), 3)

            summary = replay_research_protocol(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                output_dir,
                head=TX,
                transport=resumed_transport,
                resume=True,
            )
            self.assertEqual(resumed_calls, 2)
            self.assertEqual(summary["providerCallCount"], 5)
            self.assertEqual(summary["logicalProviderCallCount"], 5)
            self.assertEqual(summary["providerCallsPerformed"], 2)
            self.assertEqual(summary["providerCallsReusedFromCheckpoint"], 1)
            self.assertEqual(summary["providerCallsCoveredByReusedBundles"], 2)
            self.assertEqual(summary["reusedBundleCount"], 1)

            def unexpected_transport(_: dict[str, object]) -> dict[str, object]:
                raise AssertionError("a complete replay should not call the provider")

            fully_reused = replay_research_protocol(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                output_dir,
                head=TX,
                transport=unexpected_transport,
                resume=True,
            )
            self.assertEqual(fully_reused["providerCallsPerformed"], 0)
            self.assertEqual(fully_reused["providerCallsReusedFromCheckpoint"], 0)
            self.assertEqual(fully_reused["providerCallsCoveredByReusedBundles"], 5)
            self.assertEqual(fully_reused["reusedBundleCount"], 3)

    def test_validity_to_program_state_and_credit_bundle(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_transport(request: dict[str, object]) -> dict[str, object]:
            calls.append(request)
            schema = (
                request.get("response_format", {})
                .get("json_schema", {})
                .get("schema")
            )
            if schema is None:
                return response(
                    "# Rigorous audit\n\nEvery stated obligation was checked in this fixture.",
                    len(calls),
                )
            properties = schema["properties"]
            if "assessments" in properties:
                claim_keys = properties["assessments"]["items"]["properties"][
                    "claimKey"
                ]["enum"]
                value = {
                    "assessments": [
                        {
                            "claimKey": claim_key,
                            "status": "valid",
                            "premiseStatus": "not-required",
                            "summary": "The fixture accepts the exact declared claim.",
                            "scopeQualifications": [],
                            "evidenceIssues": [],
                            "evidenceTransactionIds": [],
                        }
                        for claim_key in claim_keys
                    ]
                }
                return response(json.dumps(value), len(calls))
            if "contribution" in properties:
                claim_keys = properties["contribution"]["properties"][
                    "claimKeys"
                ]["items"]["enum"]
                value = {
                    "schemaVersion": 1,
                    "operations": [
                        {
                            "entityKind": "thread",
                            "entityId": "root/gk-reduction",
                            "baseDigest": None,
                            "value": {
                                "id": "root/gk-reduction",
                                "programId": "root",
                                "title": "Auxiliary receiver reduction",
                                "summary": "Develop the structural converse reduction.",
                                "kind": "research",
                                "status": "active",
                                "expectedExposure": "4",
                                "conditions": [],
                                "sourceTransactionIds": [TX],
                            },
                        },
                        {
                            "entityKind": "item",
                            "entityId": "root/gk-foundations-result",
                            "baseDigest": None,
                            "value": {
                                "id": "root/gk-foundations-result",
                                "programId": "root",
                                "type": "result",
                                "title": "Gohari–Kramer foundations",
                                "summary": "The exact accepted structural and finite-grid result.",
                                "claimRefs": [
                                    {"transactionId": TX, "claimKey": claim_keys[0]}
                                ],
                                "sourceTransactionIds": [TX],
                                "dependencyItemIds": [],
                            },
                        },
                        {
                            "entityKind": "item",
                            "entityId": "root/gk-foundations-method",
                            "baseDigest": None,
                            "value": {
                                "id": "root/gk-foundations-method",
                                "programId": "root",
                                "type": "method",
                                "title": "Posterior-grid reduction method",
                                "summary": "The reusable method separated from the result.",
                                "claimRefs": [],
                                "sourceTransactionIds": [TX],
                                "dependencyItemIds": ["root/gk-foundations-result"],
                            },
                        },
                    ],
                    "contribution": {
                        "claimKeys": claim_keys,
                        "directProgramId": "root",
                        "directThreadIds": ["root/gk-reduction"],
                        "itemIds": [
                            "root/gk-foundations-result",
                            "root/gk-foundations-method",
                        ],
                    },
                }
                return response(json.dumps(value), len(calls))
            value = {
                "schemaVersion": 1,
                "evaluations": [
                    {
                        "programId": "root",
                        "unattributedWork": "1",
                        "rationale": "Some local causal value remains unassigned.",
                        "children": [
                            {
                                "kind": "contribution",
                                "id": TX,
                                "counterfactual": "Remove the accepted reduction and adapt from the same problem.",
                                "directEffects": [
                                    {
                                        "threadId": "root/gk-reduction",
                                        "withoutWork": "5",
                                        "withWork": "2",
                                        "rationale": "The accepted reduction saves three units locally.",
                                    }
                                ],
                                "obviatedEffects": [
                                    {
                                        "threadId": "root/unstructured-search",
                                        "withoutWork": "1",
                                        "withWork": "0.5",
                                        "rationale": "It narrows otherwise unstructured search.",
                                    }
                                ],
                                "confidence": "medium",
                                "evidenceRefs": [TX],
                            }
                        ],
                    }
                ],
            }
            return response(json.dumps(value), len(calls))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validity_dir = root / "validity"
            research_dir = root / "research"
            refresh_dir = root / "refresh"
            run_primary_judgment_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                TX,
                [TX],
                validity_dir,
                projection_root=None,
                transport=fake_transport,
            )
            run_research_update_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                TX,
                validity_dir,
                research_dir,
                transport=fake_transport,
            )
            manifest, state, credit, _ = load_research_update_bundle(research_dir)
            run_research_credit_refresh_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-hierarchical-research-v1.json",
                research_dir,
                [research_dir],
                refresh_dir,
                transport=fake_transport,
            )
            refresh_manifest, refresh_state, refresh_credit, _ = (
                load_research_credit_refresh_bundle(refresh_dir)
            )
            context = research_state_dependency_context(
                research_dir,
                PROBLEM,
                load_source(
                    ROOT,
                    PROBLEM,
                    "f236017c62c67ce4218c1f81ea34134f0954b556",
                ),
                4,
                [TX],
            )

        self.assertEqual(len(calls), 5)
        self.assertEqual(manifest["runKind"], "research-update")
        self.assertEqual(state["ledgerHead"], TX)
        self.assertEqual(state["contributions"][TX]["directProgramId"], "root")
        self.assertEqual(len(state["contributions"][TX]["claimKeys"]), 1)
        self.assertEqual(
            credit["evaluations"]["root"]["children"][0]["totalWork"],
            "3.5",
        )
        self.assertEqual(refresh_manifest["runKind"], "research-credit-refresh")
        self.assertEqual(refresh_state["stateDigest"], state["stateDigest"])
        self.assertEqual(
            refresh_credit["evaluations"]["root"]["children"][0][
                "horizonStateDigest"
            ],
            state["stateDigest"],
        )
        self.assertEqual(context["sourceKind"], "research-program-state")
        self.assertEqual(context["unresolvedDependencyTransactionIds"], [])
        self.assertIn("root/gk-foundations-result", context["selectedItems"])

    def test_invalid_submission_has_no_research_state_transition(self) -> None:
        calls = 0

        def fake_transport(request: dict[str, object]) -> dict[str, object]:
            nonlocal calls
            calls += 1
            schema = (
                request.get("response_format", {})
                .get("json_schema", {})
                .get("schema")
            )
            if schema is None:
                return response("# Audit\n\nA decisive fixture defect is present.", calls)
            claim_keys = schema["properties"]["assessments"]["items"][
                "properties"
            ]["claimKey"]["enum"]
            return response(
                json.dumps(
                    {
                        "assessments": [
                            {
                                "claimKey": key,
                                "status": "invalid",
                                "premiseStatus": "not-required",
                                "summary": "A decisive fixture defect defeats the claim.",
                                "scopeQualifications": [],
                                "evidenceIssues": ["Fixture defect."],
                                "evidenceTransactionIds": [],
                            }
                            for key in claim_keys
                        ]
                    }
                ),
                calls,
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validity_dir = root / "validity"
            run_primary_judgment_bundle(
                ROOT,
                PROBLEM,
                ROOT / "protocol/judges/openrouter-validity-judgment-v2.json",
                TX,
                [TX],
                validity_dir,
                projection_root=None,
                transport=fake_transport,
            )
            with self.assertRaisesRegex(MathFlowError, "no valid claims remain"):
                run_research_update_bundle(
                    ROOT,
                    PROBLEM,
                    ROOT
                    / "protocol/judges/openrouter-hierarchical-research-v1.json",
                    TX,
                    validity_dir,
                    root / "research",
                    transport=fake_transport,
                )
        self.assertEqual(calls, 2)


if __name__ == "__main__":
    unittest.main()
