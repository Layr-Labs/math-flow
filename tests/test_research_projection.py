from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_flow.cli import main
from math_flow.artifacts import load_manifest, read_verified_artifact, sha256_bytes
from math_flow.coordination import (
    claim_due_build,
    complete_build,
    publish_batch,
    record_completed_inputs,
)
from math_flow.credit import run_credit_assignment_bundle
from math_flow.credit_context import build_credit_context
from math_flow.judgments import (
    _validate_assessments_v3,
    _validity_v3_schema,
    load_judgment_bundle,
    run_primary_judgment_bundle,
)
from math_flow.errors import MathFlowError
from math_flow.judges import load_judge_spec, load_source
from math_flow.governance import resolve_projection
from math_flow.repository import sha256_json
from math_flow.research_credit import (
    _accepted_history,
    _allowed_credit_evidence_refs,
    _normalized_credit_decimal_matches,
    _normalized_credit_text_matches,
    _validate_credit_evidence_refs,
    load_hierarchical_credit_assignment_bundle,
)
from math_flow.research_state import empty_research_program_state
from math_flow.research_state import (
    affected_credit_targets,
    apply_research_program_batch_delta,
    credit_child_thread_ids,
    credit_children,
    materialize_credit_evaluations,
    validate_research_program_v5_batch_binding,
    validate_research_program_v5_delta,
    validate_research_program_v5_transition_shape,
)
from math_flow.research_projection import (
    _credit_schema,
    load_research_build_bundle,
    load_research_credit_refresh_bundle,
    load_research_update_bundle,
    replay_research_protocol,
    run_research_build_bundle,
    run_research_credit_refresh_bundle,
    run_research_update_bundle,
)
from math_flow.validity import (
    research_state_dependency_context,
    validate_evidence_packet_v3,
    validate_evidence_packet_v4,
)
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


def _v5_contribution_variants(request: dict[str, object]) -> list[dict[str, object]]:
    return request["response_format"]["json_schema"]["schema"]["properties"][
        "contributions"
    ]["items"]["anyOf"]


def root_only_v5_response(
    request: dict[str, object], index: int
) -> dict[str, object]:
    operations: list[dict[str, object]] = []
    contributions: list[dict[str, object]] = []
    audits: list[dict[str, object]] = []
    for variant in _v5_contribution_variants(request):
        properties = variant["properties"]
        transaction_id = properties["transactionId"]["const"]
        claim_keys = properties["claimKeys"]["items"]["enum"]
        suffix = transaction_id[:12]
        thread_id = f"root/v5-flat-line-{suffix}"
        item_id = f"root/v5-flat-result-{suffix}"
        operations.extend(
            [
                {
                    "entityKind": "thread",
                    "entityId": thread_id,
                    "baseDigest": None,
                    "value": {
                        "id": thread_id,
                        "programId": "root",
                        "title": f"Flat line {suffix}",
                        "summary": "A deliberately flat v5 fixture line.",
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
                        "title": f"Flat result {suffix}",
                        "summary": "Represent the accepted claims without hierarchy.",
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
        audits.append(
            {
                "transactionId": transaction_id,
                "basis": "canonical-objective",
                "rationale": "Deliberately exercise the root-only rejection boundary.",
                "relatedProgramIds": [],
            }
        )
    return response(
        json.dumps(
            {
                "schemaVersion": 2,
                "operations": operations,
                "contributions": contributions,
                "placementAudits": audits,
            }
        ),
        index,
    )


def hierarchical_v5_response(
    request: dict[str, object], index: int
) -> dict[str, object]:
    variants = _v5_contribution_variants(request)
    if len(variants) != 3:
        raise AssertionError("hierarchical v5 fixture expects three contributions")
    transaction_ids = [
        variant["properties"]["transactionId"]["const"] for variant in variants
    ]
    claim_keys = [
        variant["properties"]["claimKeys"]["items"]["enum"]
        for variant in variants
    ]
    analytic_tx, computational_tx, global_tx = transaction_ids
    analytic_claims, computational_claims, global_claims = claim_keys

    def program(
        program_id: str,
        parent_id: str,
        title: str,
        objective: str,
        parent_thread_id: str,
        source: str,
    ) -> dict[str, object]:
        return {
            "entityKind": "program",
            "entityId": program_id,
            "baseDigest": None,
            "value": {
                "id": program_id,
                "parentId": parent_id,
                "title": title,
                "objective": objective,
                "status": "active",
                "parentThreadIds": [parent_thread_id],
                "sourceTransactionIds": [source],
            },
        }

    def thread(
        thread_id: str,
        program_id: str,
        title: str,
        summary: str,
        source: str,
        *,
        kind: str = "research",
    ) -> dict[str, object]:
        return {
            "entityKind": "thread",
            "entityId": thread_id,
            "baseDigest": None,
            "value": {
                "id": thread_id,
                "programId": program_id,
                "title": title,
                "summary": summary,
                "kind": kind,
                "status": "active",
                "expectedExposure": "1",
                "conditions": [],
                "sourceTransactionIds": [source],
            },
        }

    def item(
        item_id: str,
        program_id: str,
        title: str,
        transaction_id: str,
        keys: list[str],
    ) -> dict[str, object]:
        return {
            "entityKind": "item",
            "entityId": item_id,
            "baseDigest": None,
            "value": {
                "id": item_id,
                "programId": program_id,
                "type": "result",
                "title": title,
                "summary": "Represent the exact accepted fixture claims.",
                "claimRefs": [
                    {"transactionId": transaction_id, "claimKey": key}
                    for key in keys
                ],
                "sourceTransactionIds": [transaction_id],
                "dependencyItemIds": [],
            },
        }

    operations = [
        thread(
            "root/analytic-agenda",
            "root",
            "Analytic agenda",
            "Develop analytic bounds and structural reductions.",
            analytic_tx,
        ),
        thread(
            "root/computational-agenda",
            "root",
            "Computational agenda",
            "Develop certified computational bounds.",
            computational_tx,
        ),
        thread(
            "root/cross-program-line",
            "root",
            "Cross-program synthesis",
            "Connect the analytic and computational agendas.",
            global_tx,
        ),
        program(
            "program/analytic",
            "root",
            "Analytic bounds",
            "Advance analytic upper bounds for the canonical capacity.",
            "root/analytic-agenda",
            analytic_tx,
        ),
        program(
            "program/computational",
            "root",
            "Certified computation",
            "Advance rigorous computational certificates for capacity bounds.",
            "root/computational-agenda",
            computational_tx,
        ),
        thread(
            "program/analytic/local-bound-agenda",
            "program/analytic",
            "Local analytic specialization",
            "Establish a specialized local analytic bound.",
            analytic_tx,
        ),
        program(
            "program/analytic/local-bound",
            "program/analytic",
            "Local analytic bound",
            "Resolve the specialized local bound inside the analytic agenda.",
            "program/analytic/local-bound-agenda",
            analytic_tx,
        ),
        thread(
            "program/analytic/unstructured-search",
            "program/analytic",
            "Unstructured analytic work",
            "Analytic work not yet assigned to a narrower thread.",
            analytic_tx,
            kind="unstructured",
        ),
        thread(
            "program/computational/unstructured-search",
            "program/computational",
            "Unstructured computational work",
            "Computational work not yet assigned to a narrower thread.",
            computational_tx,
            kind="unstructured",
        ),
        thread(
            "program/analytic/local-bound/unstructured-search",
            "program/analytic/local-bound",
            "Unstructured local-bound work",
            "Local-bound work not yet assigned to a narrower thread.",
            analytic_tx,
            kind="unstructured",
        ),
        thread(
            "program/analytic/local-bound/direct",
            "program/analytic/local-bound",
            "Direct local-bound line",
            "Track the accepted local analytic result.",
            analytic_tx,
        ),
        thread(
            "program/computational/direct",
            "program/computational",
            "Direct certificate line",
            "Track the accepted computational result.",
            computational_tx,
        ),
        item(
            "program/analytic/local-bound/result",
            "program/analytic/local-bound",
            "Accepted local analytic result",
            analytic_tx,
            analytic_claims,
        ),
        item(
            "program/computational/result",
            "program/computational",
            "Accepted computational result",
            computational_tx,
            computational_claims,
        ),
        item(
            "root/cross-program-result",
            "root",
            "Accepted cross-program result",
            global_tx,
            global_claims,
        ),
    ]
    contributions = [
        {
            "transactionId": analytic_tx,
            "claimKeys": analytic_claims,
            "directProgramId": "program/analytic/local-bound",
            "directThreadIds": ["program/analytic/local-bound/direct"],
            "itemIds": ["program/analytic/local-bound/result"],
        },
        {
            "transactionId": computational_tx,
            "claimKeys": computational_claims,
            "directProgramId": "program/computational",
            "directThreadIds": ["program/computational/direct"],
            "itemIds": ["program/computational/result"],
        },
        {
            "transactionId": global_tx,
            "claimKeys": global_claims,
            "directProgramId": "root",
            "directThreadIds": ["root/cross-program-line"],
            "itemIds": ["root/cross-program-result"],
        },
    ]
    audits = [
        {
            "transactionId": analytic_tx,
            "basis": "local-objective",
            "rationale": "The result directly advances the nested local analytic objective.",
            "relatedProgramIds": ["program/analytic/local-bound"],
        },
        {
            "transactionId": computational_tx,
            "basis": "local-objective",
            "rationale": "The result directly advances certified computation.",
            "relatedProgramIds": ["program/computational"],
        },
        {
            "transactionId": global_tx,
            "basis": "cross-program",
            "rationale": "The result directly connects incomparable analytic and computational contexts.",
            "relatedProgramIds": [
                "program/analytic/local-bound",
                "program/computational",
            ],
        },
    ]
    return response(
        json.dumps(
            {
                "schemaVersion": 2,
                "operations": operations,
                "contributions": contributions,
                "placementAudits": audits,
            }
        ),
        index,
    )


class ResearchProjectionTests(unittest.TestCase):
    def test_builder_v6_publishes_one_replayable_submission_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory_value:
            directory = Path(directory_value)
            validity = self._validity_v4_bundle(
                directory,
                PROBLEM,
                TX,
                status="valid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            _, judgment, _ = load_judgment_bundle(validity)
            builder_path = (
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v6.json"
            )
            builder = load_judge_spec(builder_path)
            projection = json.loads(
                (
                    ROOT
                    / "protocol/runtime/inactive-openrouter-research-v4-projection.json"
                ).read_text(encoding="utf-8")
            )
            scheduler = directory / "scheduler.json"
            lane = record_completed_inputs(
                scheduler,
                PROBLEM,
                f"sha256:{sha256_json(builder)}",
                [str(judgment["judgmentId"])],
                [],
                0,
                1,
                projection_spec_digest=f"sha256:{sha256_json(projection)}",
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 1)
            assert claim is not None

            calls = 0

            def v6_transport(request: dict[str, object]) -> dict[str, object]:
                nonlocal calls
                calls += 1
                content = next(
                    str(message["content"])
                    for message in request["messages"]
                    if "<math-flow-input>" in str(message["content"])
                )
                payload = json.loads(
                    content.split("<math-flow-input>\n", 1)[1].split(
                        "\n</math-flow-input>", 1
                    )[0]
                )
                subject = str(payload["subjectTransactionId"])
                claims = payload["acceptedClaims"]
                thread_id = "root/v6-fixture-line"
                item_id = "root/v6-fixture-result"
                transition = {
                    "schemaVersion": 1,
                    "subjectTransactionId": subject,
                    "baseStateDigest": payload["baseState"]["stateDigest"],
                    "contentOperations": [
                        {
                            "entityKind": "thread",
                            "entityId": thread_id,
                            "baseDigest": None,
                            "value": {
                                "id": thread_id,
                                "programId": "root",
                                "title": "Fixture line",
                                "summary": "Track the accepted fixture result.",
                                "kind": "research",
                                "status": "active",
                                "expectedExposure": "1",
                                "conditions": [],
                                "sourceTransactionIds": [subject],
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
                                "title": "Fixture result",
                                "summary": "Represent the accepted fixture claims.",
                                "claimRefs": [
                                    {
                                        "transactionId": subject,
                                        "claimKey": item["claimKey"],
                                    }
                                    for item in claims
                                ],
                                "sourceTransactionIds": [subject],
                                "dependencyItemIds": [],
                            },
                        },
                    ],
                    "topologyOperations": [],
                    "contribution": {
                        "claimKeys": sorted(
                            str(item["claimKey"]) for item in claims
                        ),
                        "directProgramId": "root",
                        "directThreadIds": [thread_id],
                        "itemIds": [item_id],
                    },
                    "placementAudit": {
                        "basis": "canonical-objective",
                        "rationale": "The fixture result is problem-global.",
                        "relatedProgramIds": [],
                    },
                    "topologyRationale": None,
                }
                if calls == 1:
                    transition["contentOperations"][-1]["value"][
                        "programId"
                    ] = "missing-program"
                else:
                    self.assertIn(
                        "root/v6-fixture-result has missing program: missing-program",
                        str(request["messages"][-1]["content"]),
                    )
                return response(
                    json.dumps(transition),
                    calls,
                )

            output = directory / "builder-v6"
            checkpoint_dir = directory / "builder-v6-checkpoints"
            run_research_build_bundle(
                ROOT,
                PROBLEM,
                builder_path,
                TX,
                claim,
                [validity],
                None,
                output,
                transport=v6_transport,
                checkpoint_dir=checkpoint_dir,
            )
            self.assertEqual(calls, 2)
            self.assertEqual(len(list(checkpoint_dir.glob("*.json"))), 1)
            manifest, state, _ = load_research_build_bundle(output)
            self.assertEqual(
                manifest["outputProfile"], "math-flow/hierarchical-research-v6"
            )
            self.assertEqual(state["schemaVersion"], 2)
            self.assertEqual(state["ledgerHead"], TX)
            self.assertEqual(set(state["contributions"]), {TX})
            self.assertEqual(len(manifest["requestDigests"]), 2)
            self.assertNotEqual(
                manifest["requestDigests"][0], manifest["requestDigests"][1]
            )
            rejected_checkpoint = checkpoint_dir / (
                manifest["requestDigests"][0].removeprefix("sha256:") + ".json"
            )
            accepted_checkpoint = checkpoint_dir / (
                manifest["requestDigests"][1].removeprefix("sha256:") + ".json"
            )
            self.assertFalse(rejected_checkpoint.exists())
            self.assertTrue(accepted_checkpoint.is_file())
            provider_run = manifest["providerRuns"][0]
            self.assertEqual(provider_run["attempts"], 2)
            self.assertEqual(
                [
                    attempt["outcome"]
                    for attempt in provider_run["attemptRecords"]
                ],
                ["validation-rejected", "accepted"],
            )
            provider_core = {
                key: value
                for key, value in provider_run.items()
                if key != "invocationDigest"
            }
            self.assertEqual(
                provider_run["invocationDigest"],
                f"sha256:{sha256_json(provider_core)}",
            )
            journal_path = (
                checkpoint_dir / "diagnostics" / "organize-attempts.json"
            )
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            journal_core = {
                key: value for key, value in journal.items() if key != "journalDigest"
            }
            self.assertEqual(
                journal["journalDigest"],
                f"sha256:{sha256_json(journal_core)}",
            )
            self.assertEqual(
                provider_run["attemptJournalDigest"], journal["journalDigest"]
            )
            self.assertEqual(
                {item["role"] for item in manifest["artifacts"]},
                {
                    "knowledge-build-input",
                    "research-builder-submission-input",
                    "submission-evidence-manifest",
                    "research-program-base-state",
                    "research-program-transition",
                    "research-program-state",
                    "research-topology-alignment",
                    "research-builder-handoff",
                },
            )

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

    def _validity_v3_bundle(
        self,
        directory: Path,
        problem: str,
        transaction_id: str,
        *,
        status: str,
        required_dependencies: list[str],
        evidence_transaction_ids: list[str],
        repository: Path = ROOT,
    ) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        spec = json.loads(
            (
                repository
                / "protocol/judges/openrouter-validity-judgment-v3.json"
            ).read_text(encoding="utf-8")
        )
        spec.pop("contextProjection")
        judge = directory / "validity-v3-spec.json"
        judge.write_text(json.dumps(spec), encoding="utf-8")
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
                return response("# Audit\n\nFixture validity-v3 audit.", calls)
            assessment_items = schema["properties"]["assessments"]["items"]
            claim_keys = [
                variant["properties"]["claimKey"]["enum"][0]
                for variant in assessment_items["anyOf"]
            ]
            return response(
                json.dumps(
                    {
                        "assessments": [
                            {
                                "claimKey": key,
                                "status": status,
                                "premiseStatus": (
                                    "not-required"
                                    if not required_dependencies
                                    else "satisfied"
                                ),
                                "summary": f"Fixture validity-v3 assessment: {status}.",
                                "scopeQualifications": [],
                                "evidenceIssues": (
                                    [] if status == "valid" else ["Fixture defect."]
                                ),
                                "evidenceTransactionIds": evidence_transaction_ids,
                                "requiredDependencyTransactionIds": required_dependencies,
                            }
                            for key in claim_keys
                        ]
                    }
                ),
                calls,
            )

        output = directory / f"validity-v3-{transaction_id[:12]}"
        run_primary_judgment_bundle(
            repository,
            problem,
            judge,
            transaction_id,
            [transaction_id],
            output,
            projection_root=None,
            transport=fake_transport,
        )
        return output

    def _validity_v4_bundle(
        self,
        directory: Path,
        problem: str,
        transaction_id: str,
        *,
        status: str,
        required_dependencies: list[str],
        evidence_transaction_ids: list[str],
        repository: Path = ROOT,
    ) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        spec = json.loads(
            (
                repository
                / "protocol/judges/openrouter-validity-judgment-v4.json"
            ).read_text(encoding="utf-8")
        )
        spec.pop("contextProjection")
        judge = directory / "validity-v4-spec.json"
        judge.write_text(json.dumps(spec), encoding="utf-8")
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
                return response("# Audit\n\nFixture validity-v4 audit.", calls)
            assessment_items = schema["properties"]["assessments"]["items"]
            claim_keys = [
                variant["properties"]["claimKey"]["enum"][0]
                for variant in assessment_items["anyOf"]
            ]
            return response(
                json.dumps(
                    {
                        "assessments": [
                            {
                                "claimKey": key,
                                "status": status,
                                "premiseStatus": (
                                    "not-required"
                                    if not required_dependencies
                                    else "satisfied"
                                ),
                                "summary": f"Fixture validity-v4 assessment: {status}.",
                                "scopeQualifications": [],
                                "evidenceIssues": (
                                    [] if status == "valid" else ["Fixture defect."]
                                ),
                                "evidenceTransactionIds": evidence_transaction_ids,
                                "requiredDependencyTransactionIds": required_dependencies,
                            }
                            for key in claim_keys
                        ]
                    }
                ),
                calls,
            )

        output = directory / f"validity-v4-{transaction_id[:12]}"
        run_primary_judgment_bundle(
            repository,
            problem,
            judge,
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

    def test_validity_v3_assessment_dependencies_are_claim_local_and_consistent(
        self,
    ) -> None:
        first_reference = "a" * 40
        second_reference = "b" * 40
        claims = [
            {
                "claimKey": "claim/first",
                "statement": "First claim.",
                "declaredReferenceTransactionIds": [first_reference],
            },
            {
                "claimKey": "claim/second",
                "statement": "Second claim.",
                "declaredReferenceTransactionIds": [second_reference],
            },
        ]
        schema = _validity_v3_schema(
            claims, [first_reference, second_reference]
        )
        variants = schema["properties"]["assessments"]["items"]["anyOf"]
        by_key = {
            variant["properties"]["claimKey"]["enum"][0]: variant
            for variant in variants
        }
        self.assertEqual(
            by_key["claim/first"]["properties"]["evidenceTransactionIds"][
                "items"
            ]["enum"],
            [first_reference],
        )
        self.assertEqual(
            by_key["claim/second"]["properties"][
                "requiredDependencyTransactionIds"
            ]["items"]["enum"],
            [second_reference],
        )

        def assessment(
            claim_key: str,
            *,
            evidence: list[str],
            required: list[str],
            premise_status: str = "not-required",
        ) -> dict[str, object]:
            return {
                "claimKey": claim_key,
                "status": "valid",
                "premiseStatus": premise_status,
                "summary": "Fixture assessment.",
                "scopeQualifications": [],
                "evidenceIssues": [],
                "evidenceTransactionIds": evidence,
                "requiredDependencyTransactionIds": required,
            }

        second = assessment(
            "claim/second", evidence=[], required=[]
        )
        with self.assertRaisesRegex(MathFlowError, "per-claim required"):
            _validate_assessments_v3(
                {
                    "assessments": [
                        assessment(
                            "claim/first",
                            evidence=[second_reference],
                            required=[second_reference],
                            premise_status="satisfied",
                        ),
                        second,
                    ]
                },
                claims,
                {first_reference, second_reference},
            )
        with self.assertRaisesRegex(MathFlowError, "same claim"):
            _validate_assessments_v3(
                {
                    "assessments": [
                        assessment(
                            "claim/first",
                            evidence=[second_reference],
                            required=[],
                        ),
                        second,
                    ]
                },
                claims,
                {first_reference, second_reference},
            )
        for required, premise_status in [
            ([first_reference], "not-required"),
            ([], "missing"),
            ([], "disputed"),
        ]:
            with self.subTest(required=required, premise_status=premise_status):
                with self.assertRaisesRegex(MathFlowError, "premise status"):
                    _validate_assessments_v3(
                        {
                            "assessments": [
                                assessment(
                                    "claim/first",
                                    evidence=required,
                                    required=required,
                                    premise_status=premise_status,
                                ),
                                second,
                            ]
                        },
                        claims,
                        {first_reference, second_reference},
                    )

    def test_validity_v3_packet_rejects_duplicate_per_claim_references(self) -> None:
        reference = "a" * 40
        core = {
            "schemaVersion": 2,
            "problemId": "demo",
            "subjectTransactionId": "c" * 40,
            "subjectLedgerPosition": 2,
            "claims": [
                {
                    "claimKey": "claim/duplicate",
                    "statement": "A claim with malformed provenance.",
                    "declaredReferenceTransactionIds": [reference, reference],
                }
            ],
            "declaredReferenceTransactionIds": [reference],
            "knowledgeContext": None,
            "objectiveAttestation": None,
        }
        packet = {
            **core,
            "packetDigest": f"sha256:{sha256_json(core)}",
        }
        with self.assertRaisesRegex(MathFlowError, "invalid claim"):
            validate_evidence_packet_v3(packet)

    def test_validity_v4_packet_rejects_unscoped_attestation(self) -> None:
        reference = "a" * 40
        unrelated = "b" * 40
        attestation = {
            "schemaVersion": 1,
            "requestDigest": "sha256:" + "1" * 64,
            "runDigest": "sha256:" + "2" * 64,
            "attestationId": "sha256:" + "3" * 64,
            "status": "passed",
            "verifier": {},
            "environmentDigest": "sha256:" + "4" * 64,
            "result": {},
            "artifacts": {},
            "stdout": {},
            "stderr": {},
        }
        core = {
            "schemaVersion": 3,
            "problemId": "demo",
            "subjectTransactionId": "c" * 40,
            "subjectLedgerPosition": 2,
            "claims": [
                {
                    "claimKey": "claim/scoped",
                    "statement": "A scoped claim.",
                    "declaredReferenceTransactionIds": [reference],
                }
            ],
            "declaredReferenceTransactionIds": [reference],
            "knowledgeContext": None,
            "objectiveAttestations": [
                {
                    "transactionId": unrelated,
                    "relation": "declared-reference",
                    "attestation": attestation,
                }
            ],
        }
        packet = {**core, "packetDigest": f"sha256:{sha256_json(core)}"}
        with self.assertRaisesRegex(MathFlowError, "invalid attestations"):
            validate_evidence_packet_v4(packet)

    def test_validity_v3_reference_to_invalid_no_three_submission_is_not_a_dependency(
        self,
    ) -> None:
        problem = "no-three-in-line-77"
        invalid_transaction = "c98dd877ad81611a9a469b1bd790cd909b56b1ce"
        self_contained_transaction = "29ccbd396781fd36d436ed2e6d0952a4730361b9"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self._validity_v3_bundle(
                root,
                problem,
                invalid_transaction,
                status="invalid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            self_contained = self._validity_v3_bundle(
                root,
                problem,
                self_contained_transaction,
                status="valid",
                required_dependencies=[],
                evidence_transaction_ids=[invalid_transaction],
            )
            self_contained_manifest, self_contained_judgment, _ = (
                load_judgment_bundle(self_contained)
            )
            packet = json.loads(
                read_verified_artifact(
                    self_contained,
                    self_contained_manifest,
                    "judgment-dependency-packet",
                )
            )
            self.assertEqual(
                packet["declaredReferenceTransactionIds"],
                [invalid_transaction],
            )
            self.assertEqual(
                self_contained_judgment["assessments"][0][
                    "requiredDependencyTransactionIds"
                ],
                [],
            )

            projection_root = root / "published"
            scheduler = projection_root / "coordination" / "scheduler.json"
            lane_output = root / "lane-v3.json"
            status = main(
                [
                    "--root",
                    str(ROOT),
                    "knowledge-trigger",
                    "--scheduler-file",
                    str(scheduler),
                    "--problem",
                    problem,
                    "--head",
                    self_contained_transaction,
                    "--builder",
                    str(
                        ROOT
                        / "protocol/judges/openrouter-hierarchical-research-builder-v3.json"
                    ),
                    "--minimum-interval",
                    "0",
                    "--judgment-dir",
                    str(self_contained),
                    "--judgment-dir",
                    str(invalid),
                    "--now",
                    "1",
                    "--output",
                    str(lane_output),
                ]
            )
            self.assertEqual(status, 0)
            lane = json.loads(lane_output.read_text(encoding="utf-8"))
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
            self.assertIsNotNone(claim)
            output = root / "research-build-v3"

            def atomic_builder_transport(
                request: dict[str, object]
            ) -> dict[str, object]:
                prompt = request["messages"][1]["content"]
                self.assertIn(
                    "Never promote an assertion, lemma, corollary",
                    prompt,
                )
                return self._batch_transport(request)

            run_research_build_bundle(
                ROOT,
                problem,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v3.json",
                self_contained_transaction,
                claim,
                [self_contained, invalid],
                None,
                output,
                transport=atomic_builder_transport,
            )
            manifest, state, build_digest = load_research_build_bundle(output)
            self.assertEqual(
                manifest["outputProfile"], "math-flow/hierarchical-research-v3"
            )
            self.assertNotIn(invalid_transaction, state["contributions"])
            self.assertEqual(
                state["contributions"][self_contained_transaction][
                    "dependencyTransactionIds"
                ],
                [],
            )
            viewer = export_viewer_data(
                ROOT,
                problem,
                self_contained_transaction,
                [output],
                judgment_dirs=[self_contained, invalid],
            )
            self.assertEqual(
                viewer["runs"][0]["judgeSpec"]["id"],
                "openrouter-hierarchical-research-builder-v3",
            )
            publish_batch(projection_root, [self_contained, invalid, output])
            complete_build(
                scheduler,
                str(lane["laneId"]),
                str(claim["buildToken"]),
                build_digest,
                2,
            )
            catalog = export_viewer_catalog(
                ROOT,
                projection_root,
                "Layr-Labs/math-flow",
                canonical_ref=self_contained_transaction,
                projection_ref="projections",
            )
            selected = next(
                item
                for item in catalog["projections"]
                if item["problemId"] == problem
            )
            self.assertEqual(
                selected["data"]["runs"][0]["judgeSpec"]["id"],
                "openrouter-hierarchical-research-builder-v3",
            )

    def test_validity_v3_required_invalid_dependency_remains_excluded(self) -> None:
        problem = "no-three-in-line-77"
        invalid_transaction = "c98dd877ad81611a9a469b1bd790cd909b56b1ce"
        dependent_transaction = "29ccbd396781fd36d436ed2e6d0952a4730361b9"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self._validity_v3_bundle(
                root,
                problem,
                invalid_transaction,
                status="invalid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            dependent = self._validity_v3_bundle(
                root,
                problem,
                dependent_transaction,
                status="valid",
                required_dependencies=[invalid_transaction],
                evidence_transaction_ids=[invalid_transaction],
            )
            builder = load_judge_spec(
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v3.json"
            )
            judgment_ids = [
                load_judgment_bundle(bundle)[1]["judgmentId"]
                for bundle in (invalid, dependent)
            ]
            scheduler = root / "scheduler-required.json"
            lane = record_completed_inputs(
                scheduler,
                problem,
                f"sha256:{sha256_json(builder)}",
                judgment_ids,
                [],
                0,
                1,
                judgment_dependencies={
                    judgment_ids[0]: [],
                    judgment_ids[1]: [judgment_ids[0]],
                },
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
            self.assertIsNotNone(claim)
            with self.assertRaisesRegex(
                MathFlowError, "submission excluded from research state"
            ):
                run_research_build_bundle(
                    ROOT,
                    problem,
                    ROOT
                    / "protocol/judges/openrouter-hierarchical-research-builder-v3.json",
                    dependent_transaction,
                    claim,
                    [invalid, dependent],
                    None,
                    root / "required-build",
                    transport=self._batch_transport,
                )

    def test_validity_v4_no_three_reference_boundary_replays_for_credit_and_viewer(
        self,
    ) -> None:
        problem = "no-three-in-line-77"
        invalid_transaction = "c98dd877ad81611a9a469b1bd790cd909b56b1ce"
        self_contained_transaction = "29ccbd396781fd36d436ed2e6d0952a4730361b9"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self._validity_v4_bundle(
                root,
                problem,
                invalid_transaction,
                status="invalid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            self_contained = self._validity_v4_bundle(
                root,
                problem,
                self_contained_transaction,
                status="valid",
                required_dependencies=[],
                evidence_transaction_ids=[invalid_transaction],
            )
            judgment_manifest, judgment, _ = load_judgment_bundle(self_contained)
            packet = json.loads(
                read_verified_artifact(
                    self_contained,
                    judgment_manifest,
                    "judgment-dependency-packet",
                )
            )
            self.assertEqual(packet["schemaVersion"], 3)
            self.assertEqual(packet["objectiveAttestations"], [])
            self.assertEqual(
                packet["declaredReferenceTransactionIds"], [invalid_transaction]
            )
            self.assertEqual(
                judgment["assessments"][0]["requiredDependencyTransactionIds"],
                [],
            )

            projection_root = root / "published"
            scheduler = projection_root / "coordination" / "scheduler.json"
            lane_output = root / "lane-v4.json"
            status = main(
                [
                    "--root",
                    str(ROOT),
                    "knowledge-trigger",
                    "--scheduler-file",
                    str(scheduler),
                    "--problem",
                    problem,
                    "--head",
                    self_contained_transaction,
                    "--builder",
                    str(
                        ROOT
                        / "protocol/judges/openrouter-hierarchical-research-builder-v4.json"
                    ),
                    "--minimum-interval",
                    "0",
                    "--judgment-dir",
                    str(self_contained),
                    "--judgment-dir",
                    str(invalid),
                    "--now",
                    "1",
                    "--output",
                    str(lane_output),
                ]
            )
            self.assertEqual(status, 0)
            lane = json.loads(lane_output.read_text(encoding="utf-8"))
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
            self.assertIsNotNone(claim)
            output = root / "research-build-v4"
            run_research_build_bundle(
                ROOT,
                problem,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v4.json",
                self_contained_transaction,
                claim,
                [invalid, self_contained],
                None,
                output,
                transport=self._batch_transport,
            )
            manifest, state, build_digest = load_research_build_bundle(output)
            self.assertEqual(
                manifest["outputProfile"], "math-flow/hierarchical-research-v4"
            )
            self.assertNotIn(invalid_transaction, state["contributions"])
            self.assertEqual(
                state["contributions"][self_contained_transaction][
                    "dependencyTransactionIds"
                ],
                [],
            )
            viewer = export_viewer_data(
                ROOT,
                problem,
                self_contained_transaction,
                [output],
                judgment_dirs=[invalid, self_contained],
            )
            self.assertEqual(
                viewer["runs"][0]["judgeSpec"]["id"],
                "openrouter-hierarchical-research-builder-v4",
            )
            publish_batch(projection_root, [invalid, self_contained, output])
            trace, history_digests, _ = _accepted_history(
                projection_root=projection_root,
                latest_run_digest=build_digest,
                latest_state=state,
            )
            self.assertEqual(history_digests, [build_digest])
            self.assertEqual(
                [
                    record["subjectTransactionId"]
                    for record in trace[0]["acceptedRecords"]
                ],
                [self_contained_transaction],
            )
            catalog = export_viewer_catalog(
                ROOT,
                projection_root,
                "Layr-Labs/math-flow",
                canonical_ref=self_contained_transaction,
                projection_ref="projections",
            )
            selected = next(
                item
                for item in catalog["projections"]
                if item["problemId"] == problem
                and item["builder"]["id"]
                == "openrouter-hierarchical-research-builder-v4"
            )
            self.assertEqual(
                selected["data"]["runs"][0]["judgeSpec"]["id"],
                "openrouter-hierarchical-research-builder-v4",
            )

    def test_validity_v4_required_premise_orders_formation(self) -> None:
        dependency_transaction = TRANSACTIONS[2]
        dependent_transaction = TRANSACTIONS[3]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dependency = self._validity_v4_bundle(
                root,
                PROBLEM,
                dependency_transaction,
                status="valid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            dependent = self._validity_v4_bundle(
                root,
                PROBLEM,
                dependent_transaction,
                status="valid",
                required_dependencies=[dependency_transaction],
                evidence_transaction_ids=[dependency_transaction],
            )
            _, dependency_judgment, _ = load_judgment_bundle(dependency)
            _, dependent_judgment, _ = load_judgment_bundle(dependent)

            independent_scheduler = root / "scheduler-independent-v4.json"
            independent_lane_output = root / "lane-independent-v4.json"
            status = main(
                [
                    "--root",
                    str(ROOT),
                    "knowledge-trigger",
                    "--scheduler-file",
                    str(independent_scheduler),
                    "--problem",
                    PROBLEM,
                    "--head",
                    dependent_transaction,
                    "--builder",
                    str(
                        ROOT
                        / "protocol/judges/openrouter-hierarchical-research-builder-v4.json"
                    ),
                    "--minimum-interval",
                    "0",
                    "--judgment-dir",
                    str(dependency),
                    "--now",
                    "1",
                    "--output",
                    str(independent_lane_output),
                ]
            )
            self.assertEqual(status, 0)
            independent_lane = json.loads(
                independent_lane_output.read_text(encoding="utf-8")
            )
            self.assertEqual(
                independent_lane["observedJudgmentIds"],
                [dependency_judgment["judgmentId"]],
            )
            self.assertIsNotNone(
                claim_due_build(
                    independent_scheduler,
                    str(independent_lane["laneId"]),
                    1,
                    500,
                )
            )

            blocked_scheduler = root / "scheduler-blocked-v4.json"
            blocked_lane_output = root / "lane-blocked-v4.json"
            status = main(
                [
                    "--root",
                    str(ROOT),
                    "knowledge-trigger",
                    "--scheduler-file",
                    str(blocked_scheduler),
                    "--problem",
                    PROBLEM,
                    "--head",
                    dependent_transaction,
                    "--builder",
                    str(
                        ROOT
                        / "protocol/judges/openrouter-hierarchical-research-builder-v4.json"
                    ),
                    "--minimum-interval",
                    "0",
                    "--judgment-dir",
                    str(dependent),
                    "--now",
                    "1",
                    "--output",
                    str(blocked_lane_output),
                ]
            )
            self.assertEqual(status, 0)
            blocked_lane = json.loads(
                blocked_lane_output.read_text(encoding="utf-8")
            )
            self.assertEqual(blocked_lane["observedJudgmentIds"], [])
            self.assertEqual(blocked_lane["pendingJudgmentIds"], [])
            self.assertIsNone(
                claim_due_build(
                    blocked_scheduler,
                    str(blocked_lane["laneId"]),
                    1,
                    500,
                )
            )

            scheduler = root / "scheduler-v4.json"
            lane_output = root / "lane-v4.json"
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
                    dependent_transaction,
                    "--builder",
                    str(
                        ROOT
                        / "protocol/judges/openrouter-hierarchical-research-builder-v4.json"
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
                    str(lane_output),
                ]
            )
            self.assertEqual(status, 0)
            lane = json.loads(lane_output.read_text(encoding="utf-8"))
            self.assertEqual(
                lane["judgmentDependencies"][dependent_judgment["judgmentId"]],
                [dependency_judgment["judgmentId"]],
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
            self.assertIsNotNone(claim)
            output = root / "ordered-build-v4"
            run_research_build_bundle(
                ROOT,
                PROBLEM,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v4.json",
                dependent_transaction,
                claim,
                [dependent, dependency],
                None,
                output,
                transport=self._batch_transport,
            )
            manifest, state, _ = load_research_build_bundle(output)
            self.assertEqual(manifest["outputProfile"], "math-flow/hierarchical-research-v4")
            self.assertEqual(
                set(state["contributions"]),
                {dependency_transaction, dependent_transaction},
            )
            self.assertEqual(
                state["contributions"][dependent_transaction][
                    "dependencyTransactionIds"
                ],
                [dependency_transaction],
            )
            batch = json.loads(
                read_verified_artifact(output, manifest, "research-batch-input")
            )
            self.assertEqual(batch["schemaVersion"], 3)

    def test_validity_v4_required_invalid_premise_stays_excluded(self) -> None:
        dependency_transaction = TRANSACTIONS[2]
        dependent_transaction = TRANSACTIONS[3]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dependency = self._validity_v4_bundle(
                root,
                PROBLEM,
                dependency_transaction,
                status="invalid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            dependent = self._validity_v4_bundle(
                root,
                PROBLEM,
                dependent_transaction,
                status="valid",
                required_dependencies=[dependency_transaction],
                evidence_transaction_ids=[dependency_transaction],
            )
            builder = load_judge_spec(
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v4.json"
            )
            judgment_ids = [
                load_judgment_bundle(bundle)[1]["judgmentId"]
                for bundle in (dependency, dependent)
            ]
            scheduler = root / "scheduler-invalid-v4.json"
            lane = record_completed_inputs(
                scheduler,
                PROBLEM,
                f"sha256:{sha256_json(builder)}",
                judgment_ids,
                [],
                0,
                1,
                judgment_dependencies={
                    judgment_ids[0]: [],
                    judgment_ids[1]: [judgment_ids[0]],
                },
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
            self.assertIsNotNone(claim)
            with self.assertRaisesRegex(
                MathFlowError, "submission excluded from research state"
            ):
                run_research_build_bundle(
                    ROOT,
                    PROBLEM,
                    ROOT
                    / "protocol/judges/openrouter-hierarchical-research-builder-v4.json",
                    dependent_transaction,
                    claim,
                    [dependent, dependency],
                    None,
                    root / "invalid-required-build-v4",
                    transport=self._batch_transport,
                )

    def test_v5_build_retries_flat_output_and_materializes_sibling_nested_credit_contexts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validity_dirs = [
                self._validity_v4_bundle(
                    root,
                    PROBLEM,
                    transaction_id,
                    status="valid",
                    required_dependencies=[],
                    evidence_transaction_ids=[],
                )
                for transaction_id in TRANSACTIONS[:3]
            ]
            builder = load_judge_spec(
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v5.json"
            )
            judgment_ids = [
                str(load_judgment_bundle(bundle)[1]["judgmentId"])
                for bundle in validity_dirs
            ]
            scheduler = root / "scheduler-v5.json"
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
            self.assertIsNotNone(claim)

            calls = 0
            rejected_flat_delta: dict[str, object] | None = None

            def correcting_transport(
                request: dict[str, object],
            ) -> dict[str, object]:
                nonlocal calls, rejected_flat_delta
                calls += 1
                if calls == 1:
                    flat_response = root_only_v5_response(request, calls)
                    rejected_flat_delta = json.loads(
                        flat_response["choices"][0]["message"]["content"]
                    )
                    return flat_response
                return hierarchical_v5_response(request, calls)

            output = root / "research-build-v5"
            checkpoint_dir = root / "checkpoints"
            run_research_build_bundle(
                ROOT,
                PROBLEM,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v5.json",
                TRANSACTIONS[2],
                claim,
                validity_dirs,
                None,
                output,
                transport=correcting_transport,
                checkpoint_dir=checkpoint_dir,
            )
            self.assertEqual(calls, 2)
            self.assertEqual(len(list(checkpoint_dir.glob("*.json"))), 1)

            manifest, state, build_digest = load_research_build_bundle(output)
            self.assertEqual(
                manifest["outputProfile"], "math-flow/hierarchical-research-v5"
            )
            self.assertEqual(
                set(state["programs"]),
                {
                    "root",
                    "program/analytic",
                    "program/computational",
                    "program/analytic/local-bound",
                },
            )
            self.assertEqual(
                credit_children(state, "root"),
                [
                    {"kind": "contribution", "id": TRANSACTIONS[2]},
                    {"kind": "program", "id": "program/analytic"},
                    {"kind": "program", "id": "program/computational"},
                ],
            )
            self.assertEqual(
                credit_children(state, "program/analytic"),
                [{"kind": "program", "id": "program/analytic/local-bound"}],
            )
            self.assertEqual(
                credit_children(state, "program/analytic/local-bound"),
                [{"kind": "contribution", "id": TRANSACTIONS[0]}],
            )
            self.assertEqual(
                set(affected_credit_targets(state, TRANSACTIONS[0])),
                {"root", "program/analytic", "program/analytic/local-bound"},
            )

            delta = json.loads(
                read_verified_artifact(output, manifest, "research-program-delta")
            )
            self.assertEqual(delta["schemaVersion"], 2)
            self.assertEqual(
                [audit["basis"] for audit in delta["placementAudits"]],
                ["local-objective", "local-objective", "cross-program"],
            )
            omitted_operation_delta = copy.deepcopy(delta)
            omitted_operation_delta["operations"] = [
                operation
                for operation in omitted_operation_delta["operations"]
                if not (
                    operation["entityKind"] == "program"
                    and operation["entityId"] == "program/analytic"
                )
            ]
            with self.assertRaisesRegex(MathFlowError, "exact materialized"):
                validate_research_program_v5_transition_shape(
                    empty_research_program_state(PROBLEM),
                    omitted_operation_delta,
                    state,
                )
            wrong_base_digest_delta = copy.deepcopy(delta)
            wrong_base_digest_delta["operations"][0]["baseDigest"] = (
                "sha256:" + "0" * 64
            )
            with self.assertRaisesRegex(MathFlowError, "exact base entity"):
                validate_research_program_v5_transition_shape(
                    empty_research_program_state(PROBLEM),
                    wrong_base_digest_delta,
                    state,
                )
            no_current_source_state = copy.deepcopy(state)
            no_current_source_thread = {
                key: value
                for key, value in no_current_source_state["threads"][
                    "root/analytic-agenda"
                ].items()
                if key != "digest"
            }
            no_current_source_thread["title"] = "Unbound historical update"
            no_current_source_state["threads"]["root/analytic-agenda"] = {
                **no_current_source_thread,
                "digest": f"sha256:{sha256_json(no_current_source_thread)}",
            }
            no_current_source_payload = {
                key: value
                for key, value in no_current_source_state.items()
                if key != "stateDigest"
            }
            no_current_source_state["stateDigest"] = (
                f"sha256:{sha256_json(no_current_source_payload)}"
            )
            no_current_source_delta = {
                "schemaVersion": 2,
                "operations": [
                    {
                        "entityKind": "thread",
                        "entityId": "root/analytic-agenda",
                        "baseDigest": state["threads"]["root/analytic-agenda"][
                            "digest"
                        ],
                        "value": no_current_source_thread,
                    }
                ],
                "contributions": [],
                "placementAudits": [],
            }
            with self.assertRaisesRegex(MathFlowError, "current accepted submission"):
                validate_research_program_v5_transition_shape(
                    state,
                    no_current_source_delta,
                    no_current_source_state,
                )
            bad_delta = copy.deepcopy(delta)
            bad_delta["placementAudits"][2]["relatedProgramIds"] = [
                "program/analytic",
                "program/analytic/local-bound",
            ]
            with self.assertRaisesRegex(MathFlowError, "incomparable"):
                validate_research_program_v5_delta(bad_delta, state)
            duplicate_cross_program_delta = copy.deepcopy(delta)
            duplicate_cross_program_delta["placementAudits"][2][
                "relatedProgramIds"
            ] = ["program/analytic", "program/analytic"]
            with self.assertRaisesRegex(MathFlowError, "unique"):
                validate_research_program_v5_delta(
                    duplicate_cross_program_delta, state
                )
            retired_cross_state = copy.deepcopy(state)
            retired_program = {
                "id": "program/retired",
                "parentId": "root",
                "title": "Retired sibling",
                "objective": "Exercise cross-program lifecycle validation.",
                "status": "retired",
                "parentThreadIds": ["root/cross-program-line"],
                "sourceTransactionIds": [TRANSACTIONS[2]],
            }
            retired_cross_state["programs"]["program/retired"] = {
                **retired_program,
                "digest": f"sha256:{sha256_json(retired_program)}",
            }
            retired_state_payload = {
                key: value
                for key, value in retired_cross_state.items()
                if key != "stateDigest"
            }
            retired_cross_state["stateDigest"] = (
                f"sha256:{sha256_json(retired_state_payload)}"
            )
            retired_cross_delta = copy.deepcopy(delta)
            retired_cross_delta["placementAudits"][2]["relatedProgramIds"] = [
                "program/analytic",
                "program/retired",
            ]
            with self.assertRaisesRegex(MathFlowError, "invalid local program"):
                validate_research_program_v5_delta(
                    retired_cross_delta, retired_cross_state
                )

            batch_input = json.loads(
                read_verified_artifact(output, manifest, "research-batch-input")
            )
            validate_research_program_v5_batch_binding(
                batch_input,
                delta,
                state,
                PROBLEM,
                problem_ledger_head=str(manifest["problemLedgerHead"]),
            )
            wrong_base_batch = copy.deepcopy(batch_input)
            wrong_base_batch["baseProgramStateDigest"] = "sha256:" + "0" * 64
            with self.assertRaisesRegex(MathFlowError, "post-state base"):
                validate_research_program_v5_batch_binding(
                    wrong_base_batch, delta, state, PROBLEM
                )
            with self.assertRaisesRegex(MathFlowError, "problem ledger head"):
                validate_research_program_v5_batch_binding(
                    batch_input,
                    delta,
                    state,
                    PROBLEM,
                    problem_ledger_head=TRANSACTIONS[3],
                )
            wrong_problem_batch = copy.deepcopy(batch_input)
            wrong_problem_batch["problemId"] = "another-problem"
            with self.assertRaisesRegex(MathFlowError, "another problem"):
                validate_research_program_v5_batch_binding(
                    wrong_problem_batch, delta, state, PROBLEM
                )
            wrong_claim_batch = copy.deepcopy(batch_input)
            wrong_claim_batch["judgments"][0]["acceptedClaimKeys"] = [
                "different-claim"
            ]
            with self.assertRaisesRegex(
                MathFlowError, "accepted judgment metadata"
            ):
                validate_research_program_v5_batch_binding(
                    wrong_claim_batch, delta, state, PROBLEM
                )
            wrong_judgment_batch = copy.deepcopy(batch_input)
            wrong_judgment_batch["judgments"][0]["judgmentId"] = (
                "sha256:" + "0" * 64
            )
            with self.assertRaisesRegex(
                MathFlowError, "accepted judgment metadata"
            ):
                validate_research_program_v5_batch_binding(
                    wrong_judgment_batch, delta, state, PROBLEM
                )

            forged_ledger = root / "forged-ledger-head-v5"
            shutil.copytree(output, forged_ledger)
            forged_ledger_manifest_path = forged_ledger / "run.json"
            forged_ledger_manifest = json.loads(
                forged_ledger_manifest_path.read_text(encoding="utf-8")
            )
            forged_ledger_manifest["problemLedgerHead"] = TRANSACTIONS[3]
            forged_ledger_manifest_path.write_text(
                json.dumps(forged_ledger_manifest, indent=2, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(MathFlowError, "problem ledger head"):
                load_research_build_bundle(forged_ledger)

            forged_base = root / "forged-batch-base-v5"
            shutil.copytree(output, forged_base)
            forged_base_batch = copy.deepcopy(batch_input)
            forged_base_batch["baseProgramStateDigest"] = "sha256:" + "0" * 64
            forged_base_batch_path = forged_base / "input" / "research-batch.json"
            forged_base_batch_bytes = (
                json.dumps(forged_base_batch, indent=2, ensure_ascii=False) + "\n"
            ).encode("utf-8")
            forged_base_batch_path.write_bytes(forged_base_batch_bytes)
            forged_base_manifest_path = forged_base / "run.json"
            forged_base_manifest = json.loads(
                forged_base_manifest_path.read_text(encoding="utf-8")
            )
            forged_base_artifact = next(
                artifact
                for artifact in forged_base_manifest["artifacts"]
                if artifact["role"] == "research-batch-input"
            )
            forged_base_artifact["digest"] = sha256_bytes(
                forged_base_batch_bytes
            )
            forged_base_artifact["bytes"] = len(forged_base_batch_bytes)
            forged_base_manifest_path.write_text(
                json.dumps(forged_base_manifest, indent=2, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(MathFlowError, "post-state base"):
                load_research_build_bundle(forged_base)

            forged = root / "forged-omitted-accepted-v5"
            shutil.copytree(output, forged)
            forged_delta = copy.deepcopy(delta)
            forged_delta["contributions"] = forged_delta["contributions"][:-1]
            forged_delta["placementAudits"] = forged_delta["placementAudits"][:-1]
            forged_delta_path = forged / "state" / "delta.json"
            forged_delta_bytes = (
                json.dumps(forged_delta, indent=2, ensure_ascii=False) + "\n"
            ).encode("utf-8")
            forged_delta_path.write_bytes(forged_delta_bytes)
            forged_manifest_path = forged / "run.json"
            forged_manifest = json.loads(
                forged_manifest_path.read_text(encoding="utf-8")
            )
            forged_artifact = next(
                artifact
                for artifact in forged_manifest["artifacts"]
                if artifact["role"] == "research-program-delta"
            )
            forged_artifact["digest"] = sha256_bytes(forged_delta_bytes)
            forged_artifact["bytes"] = len(forged_delta_bytes)
            forged_manifest_path.write_text(
                json.dumps(forged_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                MathFlowError, "do not match accepted submissions"
            ):
                load_research_build_bundle(forged)

            viewer = export_viewer_data(
                ROOT,
                PROBLEM,
                TRANSACTIONS[2],
                [output],
                judgment_dirs=validity_dirs,
            )
            self.assertEqual(
                viewer["runs"][0]["delta"]["placementAudits"],
                delta["placementAudits"],
            )
            self.assertIn(
                "program/analytic/local-bound",
                viewer["runs"][0]["state"]["nodes"],
            )
            later_source = load_source(ROOT, PROBLEM, TRANSACTIONS[3])
            dependency_context = research_state_dependency_context(
                output,
                PROBLEM,
                later_source,
                4,
                [TRANSACTIONS[0]],
            )
            self.assertEqual(
                dependency_context["unresolvedDependencyTransactionIds"], []
            )
            self.assertIn(
                "program/analytic/local-bound",
                dependency_context["selectedPrograms"],
            )

            self.assertIsNotNone(rejected_flat_delta)
            assert rejected_flat_delta is not None
            flat_state = apply_research_program_batch_delta(
                empty_research_program_state(PROBLEM),
                {
                    "schemaVersion": 1,
                    "operations": rejected_flat_delta["operations"],
                    "contributions": rejected_flat_delta["contributions"],
                },
                ledger_head=str(manifest["problemLedgerHead"]),
                accepted_claims_by_transaction={
                    str(contribution["transactionId"]): [
                        {
                            "claimKey": claim_key,
                            "dependencyTransactionIds": [],
                        }
                        for claim_key in contribution["claimKeys"]
                    ]
                    for contribution in rejected_flat_delta["contributions"]
                },
                judgment_ids={
                    transaction_id: judgment_id
                    for transaction_id, judgment_id in zip(
                        TRANSACTIONS[:3], judgment_ids, strict=True
                    )
                },
            )
            forged_flat = root / "forged-root-only-context-v5"
            shutil.copytree(output, forged_flat)
            forged_flat_manifest_path = forged_flat / "run.json"
            forged_flat_manifest = json.loads(
                forged_flat_manifest_path.read_text(encoding="utf-8")
            )
            for relative_path, role, artifact_value in (
                (
                    "state/delta.json",
                    "research-program-delta",
                    rejected_flat_delta,
                ),
                ("state/state.json", "research-program-state", flat_state),
            ):
                artifact_bytes = (
                    json.dumps(artifact_value, indent=2, ensure_ascii=False) + "\n"
                ).encode("utf-8")
                (forged_flat / relative_path).write_bytes(artifact_bytes)
                artifact_record = next(
                    artifact
                    for artifact in forged_flat_manifest["artifacts"]
                    if artifact["role"] == role
                )
                artifact_record["digest"] = sha256_bytes(artifact_bytes)
                artifact_record["bytes"] = len(artifact_bytes)
            forged_flat_manifest_path.write_text(
                json.dumps(forged_flat_manifest, indent=2, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(MathFlowError, "may not remain root-only"):
                research_state_dependency_context(
                    forged_flat,
                    PROBLEM,
                    later_source,
                    4,
                    [TRANSACTIONS[0]],
                )

            projection_root = root / "published"
            publish_batch(projection_root, [*validity_dirs, output])
            history, history_digests, references = _accepted_history(
                projection_root=projection_root,
                latest_run_digest=build_digest,
                latest_state=state,
            )
            self.assertEqual(history_digests, [build_digest])
            self.assertEqual(
                history[0]["programDelta"]["placementAudits"],
                delta["placementAudits"],
            )
            self.assertIn(
                ("root", "program", "program/analytic"), references
            )
            self.assertIn(
                (
                    "program/analytic",
                    "program",
                    "program/analytic/local-bound",
                ),
                references,
            )

            targets = {
                program_id: children
                for program_id in state["programs"]
                if (children := credit_children(state, program_id))
            }
            evaluations = []
            for program_id, children in targets.items():
                raw_children = []
                for child in children:
                    thread_ids = credit_child_thread_ids(
                        state,
                        program_id,
                        child["kind"],
                        child["id"],
                    )
                    raw_children.append(
                        {
                            "kind": child["kind"],
                            "id": child["id"],
                            "counterfactual": "Remove this local child at the common horizon.",
                            "directEffects": [
                                {
                                    "threadId": thread_id,
                                    "withoutWork": "1",
                                    "withWork": "0",
                                    "rationale": "The fixture child completes its direct line.",
                                }
                                for thread_id in thread_ids
                            ],
                            "obviatedEffects": [],
                            "confidence": "medium",
                            "evidenceRefs": [child["id"]],
                        }
                    )
                evaluations.append(
                    {
                        "programId": program_id,
                        "unattributedWork": "1",
                        "rationale": "Retain one unit of local residual work.",
                        "children": raw_children,
                    }
                )
            credit_state = materialize_credit_evaluations(
                prior_credit_state=None,
                base_program_state=state,
                post_program_state=state,
                horizon_program_state=state,
                subject_transaction_id=None,
                raw_delta={"schemaVersion": 1, "evaluations": evaluations},
                target_children_by_program=targets,
                reference_states_by_child=references,
            )
            self.assertEqual(
                set(credit_state["allocations"]), set(TRANSACTIONS[:3])
            )

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

    def test_all_invalid_v5_batch_emits_empty_audited_delta_without_provider_call(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self._validity_v4_bundle(
                root,
                PROBLEM,
                TRANSACTIONS[0],
                status="invalid",
                required_dependencies=[],
                evidence_transaction_ids=[],
            )
            builder = load_judge_spec(
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v5.json"
            )
            judgment_id = str(load_judgment_bundle(invalid)[1]["judgmentId"])
            scheduler = root / "scheduler-invalid-v5.json"
            lane = record_completed_inputs(
                scheduler,
                PROBLEM,
                f"sha256:{sha256_json(builder)}",
                [judgment_id],
                [],
                0,
                1,
            )
            claim = claim_due_build(scheduler, str(lane["laneId"]), 1, 500)
            self.assertIsNotNone(claim)

            def unexpected(_: dict[str, object]) -> dict[str, object]:
                raise AssertionError("excluded v5 judgments must not call the organizer")

            output = root / "invalid-v5-build"
            run_research_build_bundle(
                ROOT,
                PROBLEM,
                ROOT
                / "protocol/judges/openrouter-hierarchical-research-builder-v5.json",
                TRANSACTIONS[0],
                claim,
                [invalid],
                None,
                output,
                transport=unexpected,
            )
            manifest, state, _ = load_research_build_bundle(output)
            self.assertEqual(state["contributions"], {})
            self.assertEqual(manifest["providerRuns"], [])
            self.assertEqual(
                json.loads(
                    read_verified_artifact(
                        output, manifest, "research-program-delta"
                    )
                ),
                {
                    "schemaVersion": 2,
                    "operations": [],
                    "contributions": [],
                    "placementAudits": [],
                },
            )

    def test_hierarchical_credit_normalizes_representation_not_meaning(self) -> None:
        self.assertTrue(_normalized_credit_decimal_matches("1.00", "1"))
        self.assertTrue(_normalized_credit_decimal_matches("0.500", "0.5"))
        self.assertFalse(_normalized_credit_decimal_matches("1.01", "1"))
        self.assertFalse(_normalized_credit_decimal_matches("1e0", "1"))
        self.assertFalse(_normalized_credit_decimal_matches(1, "1"))
        self.assertTrue(
            _normalized_credit_text_matches("  exact rationale  ", "exact rationale")
        )
        self.assertFalse(
            _normalized_credit_text_matches("different rationale", "exact rationale")
        )
        self.assertFalse(_normalized_credit_text_matches("  ", "exact rationale"))

    def test_hierarchical_credit_enumerates_locked_evidence_refs(self) -> None:
        program_state = empty_research_program_state("no-three-in-line-77")
        transaction_id = "a" * 40
        history = [
            {
                "runDigest": "sha256:" + "b" * 64,
                "baseRunDigest": None,
                "baseProgramStateDigest": "sha256:" + "c" * 64,
                "postProgramStateDigest": program_state["stateDigest"],
                "acceptedRecords": [
                    {
                        "subjectTransactionId": transaction_id,
                        "judgmentId": "sha256:" + "d" * 64,
                        "judgmentRunDigest": "sha256:" + "e" * 64,
                    }
                ],
            }
        ]
        allowed = _allowed_credit_evidence_refs(program_state, history)
        invalid_alias = (
            "no-three-in-line-77/record-152-objective-verification"
        )
        self.assertIn(transaction_id, allowed)
        self.assertNotIn(invalid_alias, allowed)

        schema = _credit_schema(
            {"root": [{"kind": "contribution", "id": transaction_id}]},
            [],
            evidence_refs=allowed,
        )
        evidence_schema = schema["properties"]["evaluations"]["items"][
            "properties"
        ]["children"]["items"]["properties"]["evidenceRefs"]["items"]
        self.assertEqual(evidence_schema["enum"], allowed)

        with self.assertRaisesRegex(
            MathFlowError,
            "hierarchical credit cites evidence outside its locked context: "
            + invalid_alias,
        ):
            _validate_credit_evidence_refs(
                {
                    "evaluations": {
                        "root": {
                            "children": [{"evidenceRefs": [invalid_alias]}]
                        }
                    }
                },
                program_state,
                history,
            )

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
            schema_evidence_refs: list[str] = []

            def credit_transport(request: dict[str, object]) -> dict[str, object]:
                calls.append(request)
                schema = request["response_format"]["json_schema"]["schema"]
                program_ids = schema["properties"]["evaluations"]["items"][
                    "properties"
                ]["programId"]["enum"]
                self.assertEqual(program_ids, ["root"])
                allowed_evidence = schema["properties"]["evaluations"]["items"][
                    "properties"
                ]["children"]["items"]["properties"]["evidenceRefs"]["items"][
                    "enum"
                ]
                schema_evidence_refs.extend(allowed_evidence)
                self.assertNotIn(
                    "no-three-in-line-77/record-152-objective-verification",
                    allowed_evidence,
                )
                children = []
                for transaction_id in TRANSACTIONS[:2]:
                    self.assertIn(transaction_id, allowed_evidence)
                    children.append(
                        {
                            "kind": "contribution",
                            "id": transaction_id,
                            "counterfactual": "  Remove this accepted result while retaining independent information.  ",
                            "directEffects": [
                                {
                                    "threadId": f"root/batch-line-{transaction_id[:12]}",
                                    "withoutWork": "3.0",
                                    "withWork": "1.00",
                                    "rationale": "  Two units of direct local work are avoided.  ",
                                }
                            ],
                            "obviatedEffects": [
                                {
                                    "threadId": "root/unstructured-search",
                                    "withoutWork": "2.00",
                                    "withWork": "1.500",
                                    "rationale": "  The result narrows pre-existing unstructured search.  ",
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
                                    "unattributedWork": "1.0",
                                    "rationale": "  One unit remains unattributed.  ",
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
            self.assertTrue(
                all(
                    child["counterfactual"]
                    == "Remove this accepted result while retaining independent information."
                    for child in children
                )
            )
            self.assertEqual(
                credit_state["evaluations"]["root"]["unattributedWork"],
                "1",
            )
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
            self.assertIn("Allowed evidenceRefs values", prompt)
            self.assertIn(
                json.dumps(schema_evidence_refs, indent=2, ensure_ascii=False),
                prompt,
            )
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
                head=TRANSACTIONS[-1],
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
