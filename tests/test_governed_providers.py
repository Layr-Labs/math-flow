from __future__ import annotations

import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from math_flow.artifacts import sha256_bytes
from math_flow.counterfactual_context import build_submission_evidence_manifest
from math_flow.errors import MathFlowError
from math_flow.governance import validate_projection_registry, validate_projection_spec
from math_flow.governed_providers import (
    OpenRouterResearchBuilderV6Provider,
    OpenRouterWorkProjectionProvider,
    _builder_transition_schema,
    _primitive_patch_schema,
    _safe_facts_schema,
    _validate_primitive_patch_response,
    _validate_safe_response,
)
from math_flow.judges import load_judge_spec
from math_flow.research_state import empty_research_program_state
from math_flow.research_topology import derive_research_topology_alignment
from math_flow.repository import sha256_json
from math_flow.work_projection import SubmissionEvidenceFile, run_work_projection_bundle
from tests.test_research_builder_v6 import (
    JUDGMENT_A,
    TX_A,
    _accepted_claim,
    _first_transition,
)
from tests.test_work_projection import (
    ASSESSMENT,
    JUDGMENT,
    SECRET,
    TX,
    _base_accounting,
    _contract,
    _target_state,
)


ROOT = Path(__file__).resolve().parents[1]
WORK_SPEC = ROOT / "protocol/judges/openrouter-work-accounting-v1.json"
BUILDER_SPEC = ROOT / "protocol/judges/openrouter-hierarchical-research-builder-v6.json"


def _response(value: object, *, finish: str = "stop", ordinal: int = 1) -> dict[str, object]:
    return {
        "id": f"response-{ordinal}",
        "model": "openai/gpt-5.6-sol",
        "choices": [
            {
                "finish_reason": finish,
                "message": {"content": json.dumps(value)},
            }
        ],
    }


def _safe_response() -> dict[str, object]:
    return {
        "facts": [
            {
                "id": "accepted-result-exists",
                "condition": "A valid accepted result exists in the reference world.",
                "actorVisibility": "withheld-until-independent-discovery",
                "affectedNodeRefs": [
                    {"kind": "program", "id": "root"},
                    {"kind": "thread", "id": "root/unstructured-search"},
                ],
                "acceptedClaimKeys": ["main"],
            }
        ],
        "assumptions": ["Actors follow the exact root contract."],
    }


def _patch(hours: str, stage: str) -> dict[str, object]:
    return {
        "updates": [
            {
                "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                "changes": {"directWorkHours": hours},
                "rationale": f"Point estimate for the {stage} world.",
                "evidenceRefs": [f"role:{stage}"],
            }
        ]
    }


def _assert_openai_strict_schema(schema: object) -> None:
    stack = [schema]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for unsupported in ("oneOf", "uniqueItems", "minProperties"):
                if unsupported in node:
                    raise AssertionError(
                        f"strict output schema uses unsupported {unsupported}"
                    )
            if "const" in node and "type" not in node:
                raise AssertionError("strict-schema constants must declare their type")
            if "enum" in node and "type" not in node:
                raise AssertionError("strict-schema enums must declare their type")
            if node.get("type") == "object":
                properties = node.get("properties")
                if not isinstance(properties, dict):
                    raise AssertionError("strict-schema objects must declare properties")
                if node.get("additionalProperties") is not False:
                    raise AssertionError(
                        "strict-schema objects must reject additional properties"
                    )
                if set(node.get("required", [])) != set(properties):
                    raise AssertionError(
                        "strict-schema objects must require every declared property"
                    )
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


class SequentialTransport:
    def __init__(self, responses: list[dict[str, object]]):
        self.responses = list(responses)
        self.requests: list[dict[str, object]] = []

    def __call__(self, payload: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(payload))
        if not self.responses:
            raise AssertionError("unexpected provider request")
        return self.responses.pop(0)


class GovernedProviderTests(unittest.TestCase):
    def test_response_schemas_fit_openai_strict_subset(self) -> None:
        for schema in (
            _safe_facts_schema(),
            _primitive_patch_schema(),
            _builder_transition_schema(),
        ):
            _assert_openai_strict_schema(schema)

    def test_reducer_preserves_uniqueness_removed_from_provider_schema(self) -> None:
        duplicate_claim = _safe_response()
        duplicate_claim["facts"][0]["acceptedClaimKeys"] = ["main", "main"]
        with self.assertRaisesRegex(MathFlowError, "invalid accepted claim keys"):
            _validate_safe_response(duplicate_claim)

        duplicate_evidence = _patch("8", "no-access")
        duplicate_evidence["updates"][0]["evidenceRefs"] = [
            "role:no-access",
            "role:no-access",
        ]
        with self.assertRaisesRegex(MathFlowError, "audit fields"):
            _validate_primitive_patch_response(duplicate_evidence)

    def _work_fixture(self) -> SimpleNamespace:
        base_knowledge = empty_research_program_state("demo")
        target_knowledge = _target_state(base_knowledge)
        contract = _contract()
        base_accounting = _base_accounting(base_knowledge, contract)
        alignment = derive_research_topology_alignment(
            base_knowledge, target_knowledge
        )
        claims = [
            {
                "transactionId": TX,
                "claimKey": "main",
                "judgmentId": JUDGMENT,
                "assessmentDigest": ASSESSMENT,
            }
        ]
        contribution_path = "problems/demo/contributions/accepted"
        files = {
            f"{contribution_path}/README.md": (
                "# Accepted submission\n\n" + SECRET + "\n"
            ).encode(),
            f"{contribution_path}/data.bin": bytes(range(256)) * 5,
        }
        evidence_manifest, evidence_chunks = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=TX,
            contribution_path=contribution_path,
            files=files,
            chunk_bytes=41,
        )
        return SimpleNamespace(
            base_knowledge=base_knowledge,
            target_knowledge=target_knowledge,
            contract=contract,
            base_accounting=base_accounting,
            alignment=alignment,
            claims=claims,
            contribution_path=contribution_path,
            files=files,
            evidence_manifest=evidence_manifest,
            evidence_chunks=evidence_chunks,
        )

    def _run_work(self, transport: SequentialTransport):
        fixture = self._work_fixture()
        provider = OpenRouterWorkProjectionProvider(
            load_judge_spec(WORK_SPEC), transport=transport
        )
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        manifest = run_work_projection_bundle(
            output_dir=Path(temporary.name) / "bundle",
            provider=provider,
            subject_transaction_id=fixture.claims[0]["transactionId"],
            root_contract=fixture.contract,
            base_knowledge_state=fixture.base_knowledge,
            target_knowledge_state=fixture.target_knowledge,
            base_accounting_state=fixture.base_accounting,
            topology_alignment=fixture.alignment,
            evidence_manifest=fixture.evidence_manifest,
            evidence_chunks=fixture.evidence_chunks,
            accepted_claim_refs=fixture.claims,
        )
        return fixture, provider, manifest

    def test_work_roles_have_distinct_request_shapes_and_content_addresses(self) -> None:
        transport = SequentialTransport(
            [
                _response(_safe_response(), ordinal=1),
                _response(_patch("8", "no-access"), ordinal=2),
                _response(_patch("2", "with-access"), ordinal=3),
            ]
        )
        fixture, provider, manifest = self._run_work(transport)
        self.assertEqual(manifest["outputProfile"], "math-flow/work-accounting-transition-v1")
        self.assertEqual(len(provider.invocation_records), 3)
        self.assertEqual(
            [record["stage"] for record in provider.invocation_records],
            ["safe-facts", "no-access", "with-access"],
        )
        for record in provider.invocation_records:
            core = {key: value for key, value in record.items() if key != "invocationDigest"}
            self.assertEqual(record["invocationDigest"], f"sha256:{sha256_json(core)}")
            self.assertEqual(
                record["judgeSpec"]["digest"],
                f"sha256:{sha256_json(load_judge_spec(WORK_SPEC))}",
            )
            transport_identity = {
                key: value for key, value in record["transport"].items() if key != "digest"
            }
            self.assertEqual(
                record["transport"]["digest"],
                f"sha256:{sha256_json(transport_identity)}",
            )
            model_identity = {
                key: value for key, value in record["modelIdentity"].items() if key != "digest"
            }
            self.assertEqual(
                record["modelIdentity"]["digest"],
                f"sha256:{sha256_json(model_identity)}",
            )

        user_messages = [request["messages"][-1]["content"] for request in transport.requests]
        no_access = user_messages[1]
        exact_readme = fixture.files[f"{fixture.contribution_path}/README.md"]
        encoded = base64.b64encode(exact_readme).decode("ascii")
        self.assertIn(encoded, user_messages[0])
        self.assertIn(encoded, user_messages[2])
        self.assertNotIn(encoded, no_access)
        self.assertNotIn("RAW-ACTIONABLE-EVIDENCE", no_access)
        for prohibited in (
            '"evidenceManifest"',
            '"verifiedChunkDigests"',
            '"contentBase64"',
            '"entityKind":"item"',
        ):
            self.assertNotIn(prohibited, no_access)
        no_schema = transport.requests[1]["response_format"]["json_schema"]["schema"]
        rendered_schema = json.dumps(no_schema, sort_keys=True)
        self.assertNotIn("credit", rendered_schema.lower())
        self.assertNotIn("totalWork", rendered_schema)
        self.assertIn("directWorkHours", rendered_schema)

    def test_automatic_retry_rejects_truncation_without_manual_path(self) -> None:
        transport = SequentialTransport(
            [
                _response(_safe_response(), finish="length", ordinal=1),
                _response(_safe_response(), ordinal=2),
                _response(_patch("8", "no-access"), ordinal=3),
                _response(_patch("2", "with-access"), ordinal=4),
            ]
        )
        _, provider, _ = self._run_work(transport)
        self.assertEqual(len(transport.requests), 4)
        self.assertEqual(provider.invocation_records[0]["attempts"], 2)
        self.assertFalse(load_judge_spec(WORK_SPEC)["retryPolicy"]["manualReview"])

    def test_derived_work_or_credit_output_fails_closed(self) -> None:
        bad = {**_patch("8", "no-access"), "credit": "1"}
        transport = SequentialTransport(
            [
                _response(_safe_response()),
                _response(bad, ordinal=2),
                _response(bad, ordinal=3),
                _response(bad, ordinal=4),
            ]
        )
        with self.assertRaisesRegex(MathFlowError, "only primitive updates"):
            self._run_work(transport)

    def test_builder_adapter_returns_only_reducer_validated_transition(self) -> None:
        # Use the builder-v6 fixture helpers without admitting or running a projection.
        from math_flow.research_topology import empty_research_program_state_v2

        base = empty_research_program_state_v2("handoff-fixture")
        transition = _first_transition(base)
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/handoff-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )
        transport = SequentialTransport([_response(transition)])
        provider = OpenRouterResearchBuilderV6Provider(
            load_judge_spec(BUILDER_SPEC), transport=transport
        )
        output = provider.run(
            problem_id="handoff-fixture",
            subject_transaction_id=TX_A,
            base_state=base,
            accepted_claims=_accepted_claim("claim-a"),
            judgment_id=JUDGMENT_A,
            evidence_files=evidence,
        )
        self.assertEqual(output, transition)
        self.assertEqual(set(output), {
            "schemaVersion", "subjectTransactionId", "baseStateDigest",
            "contentOperations", "topologyOperations", "contribution",
            "placementAudit", "topologyRationale",
        })
        schema = transport.requests[0]["response_format"]["json_schema"]["schema"]
        self.assertEqual(
            schema["properties"]["subjectTransactionId"]["enum"],
            [TX_A],
        )
        self.assertEqual(
            schema["properties"]["baseStateDigest"]["enum"],
            [base["stateDigest"]],
        )
        rendered = json.dumps(schema, sort_keys=True)
        for derived in ("postState", "topologyAlignment", "sameWorldHandoff"):
            self.assertNotIn(derived, rendered)

    def test_builder_adapter_retries_with_deterministic_validation_feedback(self) -> None:
        from math_flow.research_topology import empty_research_program_state_v2

        base = empty_research_program_state_v2("handoff-fixture")
        corrected = _first_transition(base)
        rejected = copy.deepcopy(corrected)
        rejected["contentOperations"][-1]["value"]["programId"] = "missing-program"
        transport = SequentialTransport(
            [_response(rejected, ordinal=1), _response(corrected, ordinal=2)]
        )
        invalidations = 0

        def invalidate() -> None:
            nonlocal invalidations
            invalidations += 1

        provider = OpenRouterResearchBuilderV6Provider(
            load_judge_spec(BUILDER_SPEC),
            transport=transport,
            invalidate_last_response=invalidate,
        )
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/handoff-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )
        self.assertEqual(
            provider.run(
                problem_id="handoff-fixture",
                subject_transaction_id=TX_A,
                base_state=base,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
                evidence_files=evidence,
            ),
            corrected,
        )

        self.assertEqual(invalidations, 1)
        self.assertEqual(len(transport.requests), 2)
        self.assertEqual(
            transport.requests[0]["messages"][:3],
            transport.requests[1]["messages"][:3],
        )
        feedback = transport.requests[1]["messages"][-1]
        self.assertEqual(feedback["role"], "user")
        self.assertIn(
            "Trusted deterministic validation rejected provider attempt 1",
            feedback["content"],
        )
        self.assertIn(
            "research item v2 program-a/result-a has missing program: missing-program",
            feedback["content"],
        )
        first_digest = f"sha256:{sha256_json(transport.requests[0])}"
        second_digest = f"sha256:{sha256_json(transport.requests[1])}"
        self.assertNotEqual(first_digest, second_digest)
        self.assertEqual(
            [request["seed"] for request in transport.requests],
            [1729, 1729],
        )
        record = provider.invocation_records[0]
        self.assertEqual(record["attempts"], 2)
        self.assertEqual(record["requestDigest"], second_digest)
        attempt_records = record["attemptRecords"]
        self.assertEqual(
            [attempt["outcome"] for attempt in attempt_records],
            ["validation-rejected", "accepted"],
        )
        self.assertEqual(
            [attempt["requestDigest"] for attempt in attempt_records],
            [first_digest, second_digest],
        )
        self.assertEqual(
            attempt_records[0]["responseDigest"],
            f"sha256:{sha256_json(_response(rejected, ordinal=1))}",
        )
        self.assertEqual(attempt_records[0]["providerResponseId"], "response-1")
        self.assertRegex(attempt_records[0]["errorDigest"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(
            attempt_records[0]["feedbackDigest"],
            sha256_bytes(feedback["content"].encode("utf-8")),
        )
        self.assertEqual(
            attempt_records[1]["responseDigest"],
            f"sha256:{sha256_json(_response(corrected, ordinal=2))}",
        )
        self.assertEqual(attempt_records[1]["providerResponseId"], "response-2")
        core = {key: value for key, value in record.items() if key != "invocationDigest"}
        self.assertEqual(record["invocationDigest"], f"sha256:{sha256_json(core)}")

    def test_builder_adapter_retries_with_exact_current_base_digest(self) -> None:
        from math_flow.research_topology import empty_research_program_state_v2

        base = empty_research_program_state_v2("handoff-fixture")
        corrected = _first_transition(base)
        stale = copy.deepcopy(corrected)
        stale["baseStateDigest"] = "sha256:" + "0" * 64
        transport = SequentialTransport(
            [_response(stale, ordinal=1), _response(corrected, ordinal=2)]
        )
        provider = OpenRouterResearchBuilderV6Provider(
            load_judge_spec(BUILDER_SPEC), transport=transport
        )
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/handoff-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )

        self.assertEqual(
            provider.run(
                problem_id="handoff-fixture",
                subject_transaction_id=TX_A,
                base_state=base,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
                evidence_files=evidence,
            ),
            corrected,
        )
        feedback = str(transport.requests[1]["messages"][-1]["content"])
        self.assertIn(
            f"stale baseStateDigest; expected exact {base['stateDigest']}",
            feedback,
        )
        self.assertIn(
            f"baseStateDigest={base['stateDigest']}",
            feedback,
        )

    def test_builder_adapter_recovers_live_placement_failure_sequence(self) -> None:
        from math_flow.research_topology import empty_research_program_state_v2

        base = empty_research_program_state_v2("handoff-fixture")
        corrected = _first_transition(base)
        missing_program = copy.deepcopy(corrected)
        missing_program["contentOperations"][-1]["value"]["programId"] = (
            "missing-program"
        )
        exceptional_non_root = copy.deepcopy(corrected)
        exceptional_non_root["placementAudit"]["basis"] = "canonical-objective"
        exceptional_non_root["placementAudit"]["relatedProgramIds"] = []
        transport = SequentialTransport(
            [
                _response(missing_program, ordinal=1),
                _response(exceptional_non_root, ordinal=2),
                _response(corrected, ordinal=3),
            ]
        )
        provider = OpenRouterResearchBuilderV6Provider(
            load_judge_spec(BUILDER_SPEC), transport=transport
        )
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/handoff-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )

        self.assertEqual(
            provider.run(
                problem_id="handoff-fixture",
                subject_transaction_id=TX_A,
                base_state=base,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
                evidence_files=evidence,
            ),
            corrected,
        )
        self.assertEqual(len(transport.requests), 3)
        second_feedback = str(transport.requests[1]["messages"][-1]["content"])
        third_feedback = str(transport.requests[2]["messages"][-1]["content"])
        self.assertIn("has missing program: missing-program", second_feedback)
        self.assertIn(
            "exceptional placement applies only at root",
            third_feedback,
        )
        self.assertIn(
            "local-objective requires an active non-root directProgramId",
            third_feedback,
        )
        self.assertEqual(provider.invocation_records[0]["attempts"], 3)

    def test_builder_terminal_retries_are_distinct_bounded_and_inspectable(self) -> None:
        from math_flow.research_topology import empty_research_program_state_v2

        base = empty_research_program_state_v2("handoff-fixture")
        rejected = _first_transition(base)
        rejected["contentOperations"][-1]["value"]["programId"] = "m" * 8000
        transport = SequentialTransport(
            [_response(rejected, ordinal=ordinal) for ordinal in range(1, 4)]
        )
        invalidations = 0

        def invalidate() -> None:
            nonlocal invalidations
            invalidations += 1

        provider = OpenRouterResearchBuilderV6Provider(
            load_judge_spec(BUILDER_SPEC),
            transport=transport,
            invalidate_last_response=invalidate,
        )
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/handoff-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )
        with self.assertRaisesRegex(
            MathFlowError,
            r"failed after 3 automatic attempts; attempt journal sha256:[0-9a-f]{64}",
        ):
            provider.run(
                problem_id="handoff-fixture",
                subject_transaction_id=TX_A,
                base_state=base,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
                evidence_files=evidence,
            )

        self.assertEqual(invalidations, 3)
        self.assertEqual(len(transport.requests), 3)
        request_digests = [
            f"sha256:{sha256_json(request)}" for request in transport.requests
        ]
        self.assertEqual(len(set(request_digests)), 3)
        self.assertEqual(
            [request["seed"] for request in transport.requests],
            [1729, 1729, 1729],
        )
        feedback_messages = [
            str(message["content"])
            for request in transport.requests[1:]
            for message in request["messages"][-1:]
        ]
        self.assertEqual(len(feedback_messages), 2)
        self.assertTrue(all(len(message) < 3000 for message in feedback_messages))
        self.assertIn("provider attempt 1", feedback_messages[0])
        self.assertIn("provider attempt 2", feedback_messages[1])
        self.assertIn(
            "Each non-root program names an existing parent thread",
            feedback_messages[0],
        )
        self.assertIn(
            "contentOperations: new ID => null baseDigest; existing ID =>",
            feedback_messages[0],
        )
        self.assertIn("never stateDigest", feedback_messages[0])
        self.assertIn(
            "No parent thread is shared by active child programs",
            feedback_messages[0],
        )
        self.assertIn("exactly one active unstructured thread", feedback_messages[0])
        self.assertIn(
            "local-objective requires an active non-root directProgramId",
            feedback_messages[0],
        )
        self.assertIn(
            "canonical-objective requires directProgramId root and relatedProgramIds []",
            feedback_messages[0],
        )
        self.assertIn(
            "cross-program requires directProgramId root and at least two incomparable",
            feedback_messages[0],
        )
        self.assertIn(
            "Create: ID absent from the intermediate state and null baseDigest",
            feedback_messages[0],
        )
        self.assertIn(
            "Move/retire: existing ID and its intermediate entity digest",
            feedback_messages[0],
        )
        journal = provider.latest_attempt_journal
        self.assertIsNotNone(journal)
        assert journal is not None
        self.assertEqual(
            [record["requestDigest"] for record in journal["attemptRecords"]],
            request_digests,
        )
        self.assertEqual(
            [record["outcome"] for record in journal["attemptRecords"]],
            ["validation-rejected"] * 3,
        )
        self.assertEqual(
            [len(record["errorSummary"]) for record in journal["attemptRecords"]],
            [500, 500, 500],
        )
        self.assertTrue(
            all(
                record["errorSummary"].startswith(
                    "research item v2 program-a/result-a has missing program:"
                )
                for record in journal["attemptRecords"]
            )
        )
        self.assertEqual(provider.invocation_records, [])

    def test_builder_adapter_rejects_model_authored_alignment(self) -> None:
        from math_flow.research_topology import empty_research_program_state_v2

        base = empty_research_program_state_v2("handoff-fixture")
        bad = {**_first_transition(base), "topologyAlignment": {}}
        transport = SequentialTransport(
            [_response(bad, ordinal=ordinal) for ordinal in range(1, 4)]
        )
        provider = OpenRouterResearchBuilderV6Provider(
            load_judge_spec(BUILDER_SPEC), transport=transport
        )
        content = b"# Exact accepted submission\n"
        evidence = (
            SubmissionEvidenceFile(
                path="problems/handoff-fixture/contributions/accepted/README.md",
                digest=sha256_bytes(content),
                content=content,
            ),
        )
        with self.assertRaisesRegex(MathFlowError, "only transition operations"):
            provider.run(
                problem_id="handoff-fixture",
                subject_transaction_id=TX_A,
                base_state=base,
                accepted_claims=_accepted_claim("claim-a"),
                judgment_id=JUDGMENT_A,
                evidence_files=evidence,
            )
        self.assertEqual(len(transport.requests), 3)
        self.assertEqual(provider.invocation_records, [])

    def test_governance_accepts_candidates_and_optional_serial_admission(self) -> None:
        knowledge = {
            "schemaVersion": 1,
            "id": "candidate-research-v6",
            "description": "Inactive candidate only.",
            "status": "disabled",
            "engine": "openrouter-repository-v1",
            "allowedProblems": ["*"],
            "primaryJudge": "protocol/judges/openrouter-validity-judgment-v4.json",
            "reconciliationJudge": None,
            "knowledgeBuilder": "protocol/judges/openrouter-hierarchical-research-builder-v6.json",
            "scheduling": {
                "judgmentMaxParallel": 16,
                "knowledgeMinimumIntervalSeconds": 300,
                "maximumJudgmentsPerBuild": 500,
            },
        }
        reader = lambda relative: (ROOT / relative).read_text(encoding="utf-8")
        self.assertEqual(
            validate_projection_spec(knowledge, knowledge["id"], reader), knowledge
        )
        overlay = {
            "schemaVersion": 2,
            "id": "candidate-work-accounting-v1",
            "description": "Inactive candidate only.",
            "status": "disabled",
            "engine": "overlay-repository-v1",
            "allowedProblems": ["*"],
            "runner": {
                "implementation": "openrouter-work-accounting-v1",
                "spec": "protocol/judges/openrouter-work-accounting-v1.json",
            },
            "dependencies": [
                {
                    "name": "knowledge",
                    "projectionId": "candidate-research-v6",
                    "artifactRole": "knowledge-state",
                }
            ],
            "scheduling": {"minimumIntervalSeconds": 300},
        }
        self.assertEqual(
            validate_projection_spec(overlay, overlay["id"], reader), overlay
        )
        serial_admission = (
            ROOT / "protocol/projections/openrouter-research-v4.json"
        )
        overlay_admission = (
            ROOT / "protocol/projections/openrouter-work-accounting-v1.json"
        )
        registry = validate_projection_registry(ROOT)
        self.assertEqual(
            registry,
            {
                "projections": 9
                + int(serial_admission.exists())
                + int(overlay_admission.exists()),
                "active": 2
                + int(serial_admission.exists())
                + int(overlay_admission.exists()),
            },
        )
        registered = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "protocol/projections").glob("*.json")
        )
        if overlay_admission.exists():
            self.assertEqual(
                overlay_admission.read_bytes(),
                (
                    ROOT
                    / "protocol/runtime/active-openrouter-work-accounting-v1-projection.json"
                ).read_bytes(),
            )
            self.assertIn("openrouter-work-accounting-v1", registered)
        else:
            self.assertNotIn("openrouter-work-accounting-v1", registered)
        if serial_admission.exists():
            self.assertIn("openrouter-hierarchical-research-builder-v6", registered)
        else:
            self.assertNotIn("openrouter-hierarchical-research-builder-v6", registered)


if __name__ == "__main__":
    unittest.main()
