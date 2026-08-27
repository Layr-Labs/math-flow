from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.counterfactual_context import (
    build_impact_subgraph_context,
    build_submission_evidence_manifest,
)
from math_flow.errors import MathFlowError
from math_flow.repository import sha256_json
from math_flow.research_state import (
    apply_research_program_delta,
    empty_research_program_state,
)
from math_flow.research_topology import (
    derive_research_topology_alignment,
    empty_research_program_state_v2,
)
from math_flow.work_accounting import build_work_accounting_state, make_root_contract
from math_flow.work_projection import (
    _required_primitive_updates,
    PROFILE,
    PROFILE_V2,
    SubmissionEvidenceFile,
    load_work_projection_bundle,
    prepare_frozen_with_access_candidate_v2,
    run_work_projection_bundle,
    validate_work_projection_manifest,
)


TX = "a" * 40
OTHER_TX = "b" * 40
JUDGMENT = "sha256:" + "c" * 64
ASSESSMENT = "sha256:" + "d" * 64
PROJECTION = "sha256:" + "e" * 64
SECRET = (
    "RAW-ACTIONABLE-EVIDENCE: combine the hidden operators at alpha=137 and "
    "beta=211 to finish the construction."
)


def _target_state(base: dict[str, object]) -> dict[str, object]:
    return apply_research_program_delta(
        base,
        {
            "schemaVersion": 1,
            "operations": [
                {
                    "entityKind": "item",
                    "entityId": "root/accepted-result",
                    "baseDigest": None,
                    "value": {
                        "id": "root/accepted-result",
                        "programId": "root",
                        "type": "result",
                        "title": "Accepted result",
                        "summary": "The builder's semantic anchor for the accepted result.",
                        "claimRefs": [{"transactionId": TX, "claimKey": "main"}],
                        "sourceTransactionIds": [TX],
                        "dependencyItemIds": [],
                    },
                }
            ],
            "contribution": {
                "claimKeys": ["main"],
                "directProgramId": "root",
                "directThreadIds": ["root/unstructured-search"],
                "itemIds": ["root/accepted-result"],
            },
        },
        ledger_head=TX,
        subject_transaction_id=TX,
        accepted_claims=[
            {
                "claimKey": "main",
                "statement": "A construction exists.",
                "dependencyTransactionIds": [],
            }
        ],
        judgment_id=JUDGMENT,
    )


def _contract() -> dict[str, object]:
    return make_root_contract(
        problem_id="demo",
        knowledge_projection_id="openrouter-research-v3",
        knowledge_projection_spec_digest=PROJECTION,
        objective="Resolve the demo objective.",
        terminal_condition="The canonical objective has an accepted proof.",
        tool_baseline="Ordinary references and standard proof tools as of 2026-08-25.",
        reference_community_description="Qualified researchers organized by Math Flow's builder.",
        researcher_qualification="A researcher qualified for the local work package.",
    )


def _topology_target_state(base: dict[str, object]) -> dict[str, object]:
    return apply_research_program_delta(
        base,
        {
            "schemaVersion": 1,
            "operations": [
                {
                    "entityKind": "thread",
                    "entityId": "root/approach-entry",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach-entry",
                        "programId": "root",
                        "title": "Approach entry",
                        "summary": "The builder-owned entry point for the new program.",
                        "kind": "research",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "program",
                    "entityId": "root/approach",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach",
                        "parentId": "root",
                        "title": "Approach",
                        "objective": "Resolve the approach-specific objective.",
                        "status": "active",
                        "parentThreadIds": ["root/approach-entry"],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "thread",
                    "entityId": "root/approach/unstructured-search",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach/unstructured-search",
                        "programId": "root/approach",
                        "title": "Unstructured search",
                        "summary": "Residual work inside the new program.",
                        "kind": "unstructured",
                        "status": "active",
                        "expectedExposure": "1",
                        "conditions": [],
                        "sourceTransactionIds": [TX],
                    },
                },
                {
                    "entityKind": "item",
                    "entityId": "root/approach/result",
                    "baseDigest": None,
                    "value": {
                        "id": "root/approach/result",
                        "programId": "root/approach",
                        "type": "result",
                        "title": "Accepted result",
                        "summary": "The result organized into the new program.",
                        "claimRefs": [{"transactionId": TX, "claimKey": "main"}],
                        "sourceTransactionIds": [TX],
                        "dependencyItemIds": [],
                    },
                },
            ],
            "contribution": {
                "claimKeys": ["main"],
                "directProgramId": "root/approach",
                "directThreadIds": ["root/approach/unstructured-search"],
                "itemIds": ["root/approach/result"],
            },
        },
        ledger_head=TX,
        subject_transaction_id=TX,
        accepted_claims=[
            {
                "claimKey": "main",
                "statement": "A construction exists.",
                "dependencyTransactionIds": [],
            }
        ],
        judgment_id=JUDGMENT,
    )


def _base_accounting(
    base_knowledge: dict[str, object], contract: dict[str, object]
) -> dict[str, object]:
    return build_work_accounting_state(
        root_contract=contract,
        knowledge_state=base_knowledge,
        annotations=[
            {
                "nodeRef": {"kind": "program", "id": "root"},
                "directWorkHours": "2",
                "conditionalIncidence": None,
            },
            {
                "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                "directWorkHours": "10",
                "conditionalIncidence": "1",
            },
        ],
    )


class FakeProvider:
    def __init__(self, *, no_work: str = "8", with_work: str = "2", fail=False):
        self.no_work = no_work
        self.with_work = with_work
        self.fail = fail
        self.calls: list[tuple[str, dict[str, object], tuple[SubmissionEvidenceFile, ...]]] = []

    def __call__(self, *, stage, request, evidence_files):
        if self.fail:
            raise AssertionError("checkpointed provider should not be called")
        evidence = tuple(evidence_files)
        self.calls.append((stage, copy.deepcopy(request), evidence))
        if stage == "safe-facts":
            self.assert_complete_evidence(evidence)
            return {
                "facts": [
                    {
                        "id": "accepted-result-exists",
                        "condition": "A valid result satisfying the accepted claim exists.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": "program", "id": "root"},
                            {"kind": "thread", "id": "root/unstructured-search"},
                        ],
                        "acceptedClaimKeys": ["main"],
                    }
                ],
                "assumptions": [
                    "The counterfactual community follows the fixed root contract."
                ],
            }
        if stage == "no-access":
            if evidence:
                raise AssertionError("no-access stage received submission evidence")
            value = self.no_work
            evidence_ref = "safe-fact:accepted-result-exists"
        elif stage == "with-access":
            self.assert_complete_evidence(evidence)
            value = self.with_work
            evidence_ref = request["bindings"]["submissionEvidenceManifestDigest"]
        else:  # pragma: no cover - the runner validates its own stages
            raise AssertionError(stage)
        return {
            "updates": [
                {
                    "nodeRef": {"kind": "thread", "id": "root/unstructured-search"},
                    "changes": {"directWorkHours": value},
                    "rationale": f"The {stage} world has this residual direct work.",
                    "evidenceRefs": [evidence_ref],
                }
            ]
        }

    @staticmethod
    def assert_complete_evidence(evidence):
        contents = {item.path: item.content for item in evidence}
        if not contents or not any(SECRET.encode() in value for value in contents.values()):
            raise AssertionError("provider did not receive the exact complete submission")
        for item in evidence:
            if sha256_bytes(item.content) != item.digest:
                raise AssertionError("provider received misbound evidence")


class TopologyProvider(FakeProvider):
    def __call__(self, *, stage, request, evidence_files):
        if stage == "safe-facts":
            self.assert_complete_evidence(evidence_files)
            self.calls.append((stage, copy.deepcopy(request), tuple(evidence_files)))
            return {
                "facts": [
                    {
                        "id": "new-program-exists",
                        "condition": "A relevant route and accepted result exist in this world.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": "program", "id": "root/approach"},
                            {"kind": "thread", "id": "root/approach-entry"},
                            {
                                "kind": "thread",
                                "id": "root/approach/unstructured-search",
                            },
                        ],
                        "acceptedClaimKeys": ["main"],
                    }
                ],
                "assumptions": ["Latent work is estimated on the realized topology."],
            }
        self.calls.append((stage, copy.deepcopy(request), tuple(evidence_files)))
        if stage == "no-access" and evidence_files:
            raise AssertionError("no-access stage received submission evidence")
        if stage == "with-access":
            self.assert_complete_evidence(evidence_files)
        direct_program, direct_search = (
            ("3", "10") if stage == "no-access" else ("2", "2")
        )
        evidence_ref = f"stage:{stage}"
        return {
            "updates": [
                {
                    "nodeRef": {"kind": "program", "id": "root/approach"},
                    "changes": {
                        "directWorkHours": direct_program,
                        "conditionalIncidence": "0.5",
                    },
                    "rationale": "Estimate the newly explicit program in the same world.",
                    "evidenceRefs": [evidence_ref],
                },
                {
                    "nodeRef": {"kind": "thread", "id": "root/approach-entry"},
                    "changes": {
                        "directWorkHours": "0",
                        "conditionalIncidence": "0.5",
                    },
                    "rationale": "Estimate the builder-owned entry thread.",
                    "evidenceRefs": [evidence_ref],
                },
                {
                    "nodeRef": {
                        "kind": "thread",
                        "id": "root/approach/unstructured-search",
                    },
                    "changes": {
                        "directWorkHours": direct_search,
                        "conditionalIncidence": "1",
                    },
                    "rationale": "Estimate residual work inside the newly explicit program.",
                    "evidenceRefs": [evidence_ref],
                },
            ]
        }


class WorkProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base_knowledge = empty_research_program_state("demo")
        self.target_knowledge = _target_state(self.base_knowledge)
        self.contract = _contract()
        self.base_accounting = _base_accounting(self.base_knowledge, self.contract)
        self.alignment = derive_research_topology_alignment(
            self.base_knowledge, self.target_knowledge
        )
        self.claims = [
            {
                "transactionId": TX,
                "claimKey": "main",
                "judgmentId": JUDGMENT,
                "assessmentDigest": ASSESSMENT,
            }
        ]
        self.contribution_path = "problems/demo/contributions/accepted"
        self.files = {
            f"{self.contribution_path}/README.md": (
                "# Accepted submission\n\n" + SECRET + "\n"
            ).encode(),
            f"{self.contribution_path}/data.bin": bytes(range(256)) * 5,
        }
        self.evidence_manifest, self.evidence_chunks = (
            build_submission_evidence_manifest(
                problem_id="demo",
                subject_transaction_id=TX,
                contribution_path=self.contribution_path,
                files=self.files,
                chunk_bytes=41,
            )
        )

    def _run(self, output: Path, provider: FakeProvider, checkpoint: Path | None = None):
        return run_work_projection_bundle(
            output_dir=output,
            provider=provider,
            subject_transaction_id=TX,
            root_contract=self.contract,
            base_knowledge_state=self.base_knowledge,
            target_knowledge_state=self.target_knowledge,
            base_accounting_state=self.base_accounting,
            topology_alignment=self.alignment,
            evidence_manifest=self.evidence_manifest,
            evidence_chunks=self.evidence_chunks,
            accepted_claim_refs=self.claims,
            checkpoint_dir=checkpoint,
        )

    def _run_v2(
        self,
        output: Path,
        provider: FakeProvider,
        checkpoint: Path | None = None,
        frozen_candidate: object | None = None,
    ):
        return run_work_projection_bundle(
            output_dir=output,
            provider=provider,
            subject_transaction_id=TX,
            root_contract=self.contract,
            base_knowledge_state=self.base_knowledge,
            target_knowledge_state=self.target_knowledge,
            base_accounting_state=self.base_accounting,
            topology_alignment=self.alignment,
            evidence_manifest=self.evidence_manifest,
            evidence_chunks=self.evidence_chunks,
            accepted_claim_refs=self.claims,
            checkpoint_dir=checkpoint,
            output_profile=PROFILE_V2,
            frozen_with_access_candidate=frozen_candidate,
        )

    def test_per_submission_pipeline_firewall_and_immutable_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "bundle"
            provider = FakeProvider()
            manifest = self._run(output, provider)
            self.assertEqual(
                [call[0] for call in provider.calls],
                ["safe-facts", "no-access", "with-access"],
            )
            self.assertEqual(manifest["outputProfile"], PROFILE)
            no_request = (output / "stages/no-access/request.json").read_bytes()
            no_input = (output / "stages/no-access/input.json").read_bytes()
            self.assertNotIn(SECRET.encode(), no_request)
            self.assertNotIn(SECRET.encode(), no_input)
            self.assertNotIn(b'"evidenceManifest"', no_request)
            loaded = load_work_projection_bundle(output)
            self.assertEqual(loaded["evaluation"]["workValueHours"], "6")
            self.assertEqual(loaded["noAccessState"]["processedSubmissionIds"], [])
            self.assertEqual(loaded["withAccessState"]["processedSubmissionIds"], [TX])
            self.assertEqual(loaded["evidenceChunks"], self.evidence_chunks)

    def test_checkpoint_resume_is_provider_free_and_bundle_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = root / "checkpoints"
            first = root / "first"
            second = root / "second"
            provider = FakeProvider()
            self._run(first, provider, checkpoint)
            self.assertEqual(len(provider.calls), 3)
            self._run(second, FakeProvider(fail=True), checkpoint)
            first_files = {
                path.relative_to(first).as_posix(): path.read_bytes()
                for path in first.rglob("*")
                if path.is_file()
            }
            second_files = {
                path.relative_to(second).as_posix(): path.read_bytes()
                for path in second.rglob("*")
                if path.is_file()
            }
            self.assertEqual(first_files, second_files)
            loaded = load_work_projection_bundle(first)
            self.assertEqual(
                load_work_projection_bundle(
                    second, expected_bundle_digest=loaded["bundleDigest"]
                )["bundleDigest"],
                loaded["bundleDigest"],
            )

    def test_v2_freezes_with_access_before_direct_no_access_estimation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "bundle"
            provider = FakeProvider()
            manifest = self._run_v2(output, provider)
            self.assertEqual(
                [call[0] for call in provider.calls],
                ["safe-facts", "with-access", "no-access"],
            )
            self.assertEqual(manifest["outputProfile"], PROFILE_V2)
            no_request = provider.calls[2][1]
            stage_input = no_request["stageInput"]
            frozen = stage_input["frozenWithAccessState"]
            self.assertEqual(
                stage_input["frozenWithAccessStateDigest"], frozen["stateDigest"]
            )
            self.assertEqual(frozen["totalWorkHours"], "4")
            self.assertEqual(frozen["processedSubmissionIds"], [TX])
            self.assertEqual(frozen["predecessorStateDigest"], self.base_accounting["stateDigest"])
            rendered_no_request = json.dumps(no_request, sort_keys=True)
            self.assertNotIn(SECRET, rendered_no_request)
            self.assertNotIn("evidenceManifest", rendered_no_request)
            self.assertNotIn("withAccessPatch", rendered_no_request)
            self.assertNotIn("rationale", json.dumps(frozen, sort_keys=True))
            loaded = load_work_projection_bundle(output)
            self.assertEqual(loaded["evaluation"]["workValueHours"], "6")
            self.assertEqual(loaded["withAccessState"], frozen)
            self.assertEqual(
                manifest["responseDigests"][1]["stage"], "with-access"
            )
            self.assertEqual(manifest["responseDigests"][2]["stage"], "no-access")

    def test_v2_nonpositive_retry_reuses_frozen_w_plus_and_only_recalls_w_minus(self) -> None:
        class NoAccessRetryProvider(FakeProvider):
            def __call__(self, *, stage, request, evidence_files):
                if stage != "no-access":
                    raise AssertionError("validated W+ must not be regenerated")
                return super().__call__(
                    stage=stage, request=request, evidence_files=evidence_files
                )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = root / "checkpoints"
            first = FakeProvider(no_work="2", with_work="8")
            with self.assertRaisesRegex(MathFlowError, "strictly positive"):
                self._run_v2(root / "first", first, checkpoint)
            self.assertEqual(
                [call[0] for call in first.calls],
                ["safe-facts", "with-access", "no-access"],
            )
            retry = NoAccessRetryProvider(no_work="12", with_work="999")
            self._run_v2(root / "second", retry, checkpoint)
            self.assertEqual([call[0] for call in retry.calls], ["no-access"])
            loaded = load_work_projection_bundle(root / "second")
            self.assertEqual(loaded["withAccessState"]["totalWorkHours"], "10")
            self.assertEqual(loaded["evaluation"]["workValueHours"], "4")

    def test_v2_frozen_candidate_rejects_tampered_predecessor_and_processed_state(self) -> None:
        provider = FakeProvider()
        candidate = prepare_frozen_with_access_candidate_v2(
            provider=provider,
            subject_transaction_id=TX,
            root_contract=self.contract,
            base_knowledge_state=self.base_knowledge,
            target_knowledge_state=self.target_knowledge,
            base_accounting_state=self.base_accounting,
            topology_alignment=self.alignment,
            evidence_manifest=self.evidence_manifest,
            evidence_chunks=self.evidence_chunks,
            accepted_claim_refs=self.claims,
        )
        self.assertEqual([call[0] for call in provider.calls], ["safe-facts", "with-access"])

        stale = copy.deepcopy(candidate)
        state = stale["withAccessState"]
        state["predecessorStateDigest"] = "sha256:" + "1" * 64
        state_core = {key: value for key, value in state.items() if key != "stateDigest"}
        state["stateDigest"] = "sha256:" + sha256_json(state_core)
        stale_core = {key: value for key, value in stale.items() if key != "candidateDigest"}
        stale["candidateDigest"] = "sha256:" + sha256_json(stale_core)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(MathFlowError, "stale live predecessor"):
                self._run_v2(Path(temporary) / "stale", FakeProvider(), frozen_candidate=stale)

        wrong_processed = copy.deepcopy(candidate)
        wrong_state = wrong_processed["withAccessState"]
        wrong_state["processedSubmissionIds"] = []
        wrong_state_core = {
            key: value for key, value in wrong_state.items() if key != "stateDigest"
        }
        wrong_state["stateDigest"] = "sha256:" + sha256_json(wrong_state_core)
        wrong_core = {
            key: value
            for key, value in wrong_processed.items()
            if key != "candidateDigest"
        }
        wrong_processed["candidateDigest"] = "sha256:" + sha256_json(wrong_core)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(MathFlowError, "append its subject"):
                self._run_v2(
                    Path(temporary) / "processed",
                    FakeProvider(),
                    frozen_candidate=wrong_processed,
                )

    def test_same_world_estimation_handles_new_builder_nodes(self) -> None:
        target = _topology_target_state(self.base_knowledge)
        alignment = derive_research_topology_alignment(self.base_knowledge, target)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "bundle"
            provider = TopologyProvider()
            run_work_projection_bundle(
                output_dir=output,
                provider=provider,
                subject_transaction_id=TX,
                root_contract=self.contract,
                base_knowledge_state=self.base_knowledge,
                target_knowledge_state=target,
                base_accounting_state=self.base_accounting,
                topology_alignment=alignment,
                evidence_manifest=self.evidence_manifest,
                evidence_chunks=self.evidence_chunks,
                accepted_claim_refs=self.claims,
            )
            loaded = load_work_projection_bundle(output)
            self.assertEqual(loaded["evaluation"]["workValueHours"], "4.5")
            no_request = json.loads(
                (output / "stages/no-access/request.json").read_text()
            )
            self.assertEqual(
                [
                    item["nodeRef"]
                    for item in no_request["requiredPrimitiveUpdates"]
                ],
                [
                    {"kind": "program", "id": "root/approach"},
                    {"kind": "thread", "id": "root/approach-entry"},
                    {
                        "kind": "thread",
                        "id": "root/approach/unstructured-search",
                    },
                ],
            )

    def test_inactive_zeroing_is_required_only_with_access(self) -> None:
        after = copy.deepcopy(self.target_knowledge)
        thread = after["threads"]["root/unstructured-search"]
        thread["status"] = "completed"
        thread["expectedExposure"] = "0"
        thread_content = {
            key: value for key, value in thread.items() if key != "digest"
        }
        thread["digest"] = "sha256:" + sha256_json(thread_content)
        state_content = {key: value for key, value in after.items() if key != "stateDigest"}
        after["stateDigest"] = "sha256:" + sha256_json(state_content)

        self.assertEqual(
            _required_primitive_updates(
                self.base_knowledge,
                after,
                self.base_accounting,
                evaluation_mode="no-access",
            ),
            [],
        )
        self.assertEqual(
            _required_primitive_updates(
                self.base_knowledge,
                after,
                self.base_accounting,
                evaluation_mode="with-access",
            ),
            [
                {
                    "nodeRef": {
                        "kind": "thread",
                        "id": "root/unstructured-search",
                    },
                    "requiredChanges": [
                        "conditionalIncidence",
                        "directWorkHours",
                    ],
                    "reasons": ["inactive-zeroing"],
                }
            ],
        )

    def test_checkpoint_tampering_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = root / "checkpoints"
            self._run(root / "first", FakeProvider(), checkpoint)
            cached = sorted(checkpoint.glob("*.json"))[0]
            envelope = json.loads(cached.read_text())
            envelope["responseDigest"] = "sha256:" + "0" * 64
            cached.write_text(json.dumps(envelope))
            with self.assertRaisesRegex(MathFlowError, "checkpoint binding mismatch"):
                self._run(root / "second", FakeProvider(fail=True), checkpoint)

    def test_nonpositive_value_is_rejected_without_clamping_or_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "bundle"
            with self.assertRaisesRegex(MathFlowError, "strictly positive"):
                self._run(output, FakeProvider(no_work="2", with_work="8"))
            self.assertFalse(output.exists())

    def test_exactly_one_accepted_subject_and_exact_alignment_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "bundle"
            with self.assertRaisesRegex(MathFlowError, "exactly its one subject"):
                run_work_projection_bundle(
                    output_dir=output,
                    provider=FakeProvider(),
                    subject_transaction_id=OTHER_TX,
                    root_contract=self.contract,
                    base_knowledge_state=self.base_knowledge,
                    target_knowledge_state=self.target_knowledge,
                    base_accounting_state=self.base_accounting,
                    topology_alignment=self.alignment,
                    evidence_manifest=self.evidence_manifest,
                    evidence_chunks=self.evidence_chunks,
                    accepted_claim_refs=self.claims,
                )
            bad_alignment = copy.deepcopy(self.alignment)
            bad_alignment["created"] = []
            with self.assertRaisesRegex(MathFlowError, "differs from the deterministic"):
                run_work_projection_bundle(
                    output_dir=output,
                    provider=FakeProvider(),
                    subject_transaction_id=TX,
                    root_contract=self.contract,
                    base_knowledge_state=self.base_knowledge,
                    target_knowledge_state=self.target_knowledge,
                    base_accounting_state=self.base_accounting,
                    topology_alignment=bad_alignment,
                    evidence_manifest=self.evidence_manifest,
                    evidence_chunks=self.evidence_chunks,
                    accepted_claim_refs=self.claims,
                )

    def test_bundle_digest_binding_and_path_escape_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "bundle"
            self._run(output, FakeProvider())
            with self.assertRaisesRegex(MathFlowError, "content address"):
                load_work_projection_bundle(
                    output, expected_bundle_digest="sha256:" + "0" * 64
                )
            run_path = output / "run.json"
            run = json.loads(run_path.read_text())
            run["artifacts"][0]["path"] = "../escape.json"
            run_path.write_text(json.dumps(run))
            with self.assertRaisesRegex(MathFlowError, "invalid artifact path"):
                load_work_projection_bundle(output)

    def test_manifest_shape_and_schema_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._run(Path(temporary) / "bundle", FakeProvider())
            validate_work_projection_manifest(manifest)
        root = Path(__file__).resolve().parents[1]
        for name in (
            "work-projection-request-v1.schema.json",
            "work-projection-bundle-v1.schema.json",
            "work-projection-request-v2.schema.json",
            "work-projection-bundle-v2.schema.json",
            "no-access-stage-input-v2.schema.json",
            "frozen-with-access-candidate-v2.schema.json",
        ):
            value = json.loads((root / "protocol/schemas" / name).read_text())
            self.assertEqual(value["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_counterfactual_context_accepts_versioned_builder_topology(self) -> None:
        state = empty_research_program_state_v2("demo")
        context = build_impact_subgraph_context(
            problem_id="demo",
            subject_transaction_id=TX,
            accepted_claim_refs=self.claims,
            research_state=state,
            seed_node_refs=[{"kind": "program", "id": "root"}],
        )
        self.assertEqual(context["knowledgeStateDigest"], state["stateDigest"])


if __name__ == "__main__":
    unittest.main()
