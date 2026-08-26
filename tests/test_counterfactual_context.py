from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.counterfactual_context import (
    accepted_claim_refs_from_validity,
    assemble_with_access_evidence,
    build_counterfactual_safe_facts,
    build_impact_subgraph_context,
    build_no_access_stage_input,
    build_submission_evidence_manifest,
    build_with_access_stage_input,
    reconstruct_submission_evidence,
    validate_counterfactual_safe_facts,
    validate_impact_subgraph_context,
    validate_no_access_stage_input,
    validate_submission_evidence_manifest,
    validate_with_access_stage_input,
)
from math_flow.errors import MathFlowError
from math_flow.research_state import empty_research_program_state
from math_flow.repository import sha256_json


TX = "a" * 40
OTHER_TX = "b" * 40
JUDGMENT = "sha256:" + "c" * 64
ASSESSMENT = "sha256:" + "d" * 64
SECRET = (
    "ACTIONABLE-SUBMISSION-SECRET: execute the hidden spectral construction "
    "with parameters alpha=137 and beta=211; this sentence must never enter "
    "the no-access request."
)


def _record(value: dict[str, object]) -> dict[str, object]:
    return {**value, "digest": "sha256:" + sha256_json(value)}


def _branching_state() -> dict[str, object]:
    state = empty_research_program_state("demo")
    programs = {
        "root": state["programs"]["root"],
        "route-a": _record(
            {
                "id": "route-a",
                "parentId": "root",
                "title": "Route A",
                "objective": "Resolve route A.",
                "status": "active",
                "parentThreadIds": ["root/route-a-entry"],
                "sourceTransactionIds": [TX],
            }
        ),
        "route-a/deep": _record(
            {
                "id": "route-a/deep",
                "parentId": "route-a",
                "title": "Deep route",
                "objective": "Resolve the deeper route.",
                "status": "active",
                "parentThreadIds": ["route-a/deep-entry"],
                "sourceTransactionIds": [TX],
            }
        ),
        "route-b": _record(
            {
                "id": "route-b",
                "parentId": "root",
                "title": "Route B",
                "objective": "Resolve route B.",
                "status": "active",
                "parentThreadIds": ["root/route-b-entry"],
                "sourceTransactionIds": [TX],
            }
        ),
    }

    def thread(thread_id: str, program_id: str, kind: str = "unstructured"):
        return _record(
            {
                "id": thread_id,
                "programId": program_id,
                "title": f"Thread {thread_id}",
                "summary": "Builder-owned thread summary.",
                "kind": kind,
                "status": "active",
                "expectedExposure": "1",
                "conditions": [],
                "sourceTransactionIds": [TX],
            }
        )

    threads = {
        "root/unstructured-search": state["threads"]["root/unstructured-search"],
        "root/route-a-entry": thread("root/route-a-entry", "root", "research"),
        "root/route-b-entry": thread("root/route-b-entry", "root", "research"),
        "route-a/unstructured-search": thread(
            "route-a/unstructured-search", "route-a"
        ),
        "route-a/deep-entry": thread("route-a/deep-entry", "route-a", "research"),
        "route-a/deep/unstructured-search": thread(
            "route-a/deep/unstructured-search", "route-a/deep"
        ),
        "route-b/unstructured-search": thread(
            "route-b/unstructured-search", "route-b"
        ),
    }
    item = _record(
        {
            "id": "route-a/result",
            "programId": "route-a",
            "type": "result",
            "title": "Accepted result",
            "summary": "A semantic evidence anchor.",
            "claimRefs": [{"transactionId": TX, "claimKey": "main"}],
            "sourceTransactionIds": [TX],
            "dependencyItemIds": [],
        }
    )
    contribution = _record(
        {
            "id": TX,
            "transactionId": TX,
            "claimKeys": ["main"],
            "directProgramId": "route-a",
            "directThreadIds": ["route-a/unstructured-search"],
            "itemIds": ["route-a/result"],
            "dependencyTransactionIds": [],
            "judgmentId": JUDGMENT,
        }
    )
    core = {
        "schemaVersion": 1,
        "problemId": "demo",
        "ledgerHead": TX,
        "baseStateDigest": state["stateDigest"],
        "rootProgramId": "root",
        "programs": programs,
        "threads": threads,
        "items": {"route-a/result": item},
        "contributions": {TX: contribution},
    }
    return {**core, "stateDigest": "sha256:" + sha256_json(core)}


class CounterfactualContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = "problems/demo/contributions/example"
        self.files = {
            f"{self.path}/README.md": (
                "# Accepted contribution\n\n" + SECRET + "\n"
            ).encode(),
            f"{self.path}/data.bin": bytes(range(256)) * 3,
            f"{self.path}/notes/a.txt": b"supporting evidence\n" * 11,
        }
        self.manifest, self.chunks = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=TX,
            contribution_path=self.path,
            files=self.files,
            chunk_bytes=37,
        )
        self.state = empty_research_program_state("demo")
        self.claims = [
            {
                "transactionId": TX,
                "claimKey": "main",
                "judgmentId": JUDGMENT,
                "assessmentDigest": ASSESSMENT,
            }
        ]
        self.extracted = {
            "facts": [
                {
                    "id": "main-exists",
                    "condition": "A valid construction achieving the accepted claim exists.",
                    "actorVisibility": "withheld-until-independent-discovery",
                    "affectedNodeRefs": [{"kind": "program", "id": "root"}],
                    "acceptedClaimKeys": ["main"],
                }
            ],
            "assumptions": ["The pre-submission community follows its existing policy."],
        }
        self.safe = build_counterfactual_safe_facts(
            problem_id="demo",
            subject_transaction_id=TX,
            accepted_claim_refs=self.claims,
            research_state=self.state,
            evidence_manifest=self.manifest,
            evidence_chunks=self.chunks,
            extracted=self.extracted,
        )
        self.context = build_impact_subgraph_context(
            problem_id="demo",
            subject_transaction_id=TX,
            accepted_claim_refs=self.claims,
            research_state=self.state,
            seed_node_refs=[{"kind": "program", "id": "root"}],
        )

    def test_manifest_is_deterministic_metadata_and_reconstructs_all_bytes(self) -> None:
        reordered = dict(reversed(list(self.files.items())))
        second_manifest, second_chunks = build_submission_evidence_manifest(
            problem_id="demo",
            subject_transaction_id=TX,
            contribution_path=self.path,
            files=reordered,
            chunk_bytes=37,
        )
        self.assertEqual(second_manifest, self.manifest)
        self.assertEqual(second_chunks, self.chunks)
        self.assertNotIn(SECRET, json.dumps(self.manifest))
        self.assertEqual(reconstruct_submission_evidence(self.manifest, self.chunks), self.files)
        self.assertEqual(
            [item["path"] for item in self.manifest["files"]], sorted(self.files)
        )

    def test_manifest_rejects_missing_truncated_mismatched_and_extra_chunks(self) -> None:
        digest = sorted(self.chunks)[0]
        missing = dict(self.chunks)
        missing.pop(digest)
        with self.assertRaisesRegex(MathFlowError, "missing chunk"):
            reconstruct_submission_evidence(self.manifest, missing)

        truncated = dict(self.chunks)
        truncated[digest] = truncated[digest][:-1]
        with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
            reconstruct_submission_evidence(self.manifest, truncated)

        extra = {**self.chunks, "sha256:" + "e" * 64: b"undeclared"}
        with self.assertRaisesRegex(MathFlowError, "undeclared chunk"):
            reconstruct_submission_evidence(self.manifest, extra)

        tampered = copy.deepcopy(self.manifest)
        tampered["files"][0]["chunks"][0]["bytes"] -= 1
        tampered["manifestDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in tampered.items() if key != "manifestDigest"}
        )
        with self.assertRaisesRegex(MathFlowError, "truncated interior chunk"):
            validate_submission_evidence_manifest(tampered)

    def test_manifest_rejects_untrusted_path_traversal(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "safe repository path"):
            build_submission_evidence_manifest(
                problem_id="demo",
                subject_transaction_id=TX,
                contribution_path="problems/demo/contributions/../escape",
                files=self.files,
            )
        malicious_files = {
            f"{self.path}/README.md": b"valid readme",
            "problems/demo/secret.txt": b"escape",
        }
        with self.assertRaisesRegex(MathFlowError, "escapes contribution"):
            build_submission_evidence_manifest(
                problem_id="demo",
                subject_transaction_id=TX,
                contribution_path=self.path,
                files=malicious_files,
            )

    def test_safe_fact_boundary_rejects_raw_copy_and_malicious_fields(self) -> None:
        copied = copy.deepcopy(self.extracted)
        copied["facts"][0]["condition"] = SECRET
        with self.assertRaisesRegex(MathFlowError, "copy a raw submission"):
            build_counterfactual_safe_facts(
                problem_id="demo",
                subject_transaction_id=TX,
                accepted_claim_refs=self.claims,
                research_state=self.state,
                evidence_manifest=self.manifest,
                evidence_chunks=self.chunks,
                extracted=copied,
            )

        malicious = copy.deepcopy(self.extracted)
        malicious["rawSubmission"] = SECRET
        with self.assertRaisesRegex(MathFlowError, "unexpected fields"):
            build_counterfactual_safe_facts(
                problem_id="demo",
                subject_transaction_id=TX,
                accepted_claim_refs=self.claims,
                research_state=self.state,
                evidence_manifest=self.manifest,
                evidence_chunks=self.chunks,
                extracted=malicious,
            )

        actor_visible = copy.deepcopy(self.extracted)
        actor_visible["facts"][0]["actorVisibility"] = "visible"
        with self.assertRaisesRegex(MathFlowError, "must remain hidden"):
            build_counterfactual_safe_facts(
                problem_id="demo",
                subject_transaction_id=TX,
                accepted_claim_refs=self.claims,
                research_state=self.state,
                evidence_manifest=self.manifest,
                evidence_chunks=self.chunks,
                extracted=actor_visible,
            )

    def test_safe_facts_bind_subject_claim_state_and_manifest(self) -> None:
        self.assertEqual(self.safe["subjectTransactionId"], TX)
        self.assertEqual(self.safe["acceptedClaimRefs"], self.claims)
        self.assertEqual(self.safe["knowledgeStateDigest"], self.state["stateDigest"])
        self.assertEqual(
            self.safe["subjectEvidenceManifestDigest"], self.manifest["manifestDigest"]
        )
        tampered = copy.deepcopy(self.safe)
        tampered["subjectTransactionId"] = OTHER_TX
        with self.assertRaises(MathFlowError):
            validate_counterfactual_safe_facts(tampered)

    def test_validity_claim_identity_excludes_claim_statements(self) -> None:
        assessment = {
            "claimKey": "main",
            "status": "valid",
            "premiseStatus": "not-required",
            "summary": SECRET,
            "scopeQualifications": [],
            "evidenceIssues": [],
            "evidenceTransactionIds": [],
            "requiredDependencyTransactionIds": [],
        }
        refs = accepted_claim_refs_from_validity(
            {
                "schemaVersion": 4,
                "judgmentId": JUDGMENT,
                "subjects": [{"kind": "transaction", "id": TX, "ledgerPosition": 1}],
                "assessments": [assessment],
            },
            subject_transaction_id=TX,
        )
        self.assertEqual(refs[0]["claimKey"], "main")
        self.assertEqual(refs[0]["assessmentDigest"], "sha256:" + sha256_json(assessment))
        self.assertNotIn(SECRET, json.dumps(refs))

    def test_impact_context_is_deterministic_and_rejects_context_escape(self) -> None:
        second = build_impact_subgraph_context(
            problem_id="demo",
            subject_transaction_id=TX,
            accepted_claim_refs=list(reversed(self.claims)),
            research_state=self.state,
            seed_node_refs=[{"kind": "program", "id": "root"}],
        )
        self.assertEqual(second, self.context)
        self.assertEqual(
            {node["ref"]["kind"] for node in self.context["includedNodes"]},
            {"program", "thread"},
        )
        with self.assertRaises(MathFlowError):
            build_impact_subgraph_context(
                problem_id="demo",
                subject_transaction_id=TX,
                accepted_claim_refs=self.claims,
                research_state=self.state,
                seed_node_refs=[{"kind": "program", "id": "../../private"}],
            )

        tampered = copy.deepcopy(self.context)
        tampered["boundarySummaries"] = [
            {
                "nodeRef": {"kind": "program", "id": "outside"},
                "parentRef": {"kind": "program", "id": "root"},
                "relationship": "collapsed-descendant-subtree",
                "programCount": 1,
                "threadCount": 0,
                "itemCount": 0,
                "recordDigest": "sha256:" + "f" * 64,
            }
        ]
        tampered["contextDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in tampered.items() if key != "contextDigest"}
        )
        # Syntactic validation alone cannot resolve a digest-bound external
        # state, but the stage builder re-derives context from that exact state.
        validate_impact_subgraph_context(tampered)
        with self.assertRaisesRegex(MathFlowError, "escapes the exact builder topology"):
            build_no_access_stage_input(
                safe_facts=self.safe,
                impact_context=tampered,
                research_state=self.state,
            )

    def test_impact_context_collapses_remote_subtree_and_keeps_items_semantic(self) -> None:
        state = _branching_state()
        context = build_impact_subgraph_context(
            problem_id="demo",
            subject_transaction_id=TX,
            accepted_claim_refs=self.claims,
            research_state=state,
            seed_node_refs=[{"kind": "program", "id": "route-a"}],
            descendant_depth=0,
        )
        included = {
            (node["ref"]["kind"], node["ref"]["id"])
            for node in context["includedNodes"]
        }
        self.assertIn(("program", "root"), included)
        self.assertIn(("program", "route-a"), included)
        self.assertIn(("program", "route-b"), included)
        self.assertNotIn(("program", "route-a/deep"), included)
        self.assertEqual(
            context["boundarySummaries"],
            [
                {
                    "nodeRef": {"kind": "program", "id": "route-a/deep"},
                    "parentRef": {"kind": "program", "id": "route-a"},
                    "relationship": "collapsed-descendant-subtree",
                    "programCount": 1,
                    "threadCount": 1,
                    "itemCount": 0,
                    "recordDigest": state["programs"]["route-a/deep"]["digest"],
                }
            ],
        )
        self.assertEqual(
            [item["itemId"] for item in context["semanticItemRefs"]],
            ["route-a/result"],
        )
        self.assertTrue(
            all(node["ref"]["kind"] != "item" for node in context["includedNodes"])
        )

    def test_no_access_has_structural_and_byte_level_firewall(self) -> None:
        no_access = build_no_access_stage_input(
            safe_facts=self.safe,
            impact_context=self.context,
            research_state=self.state,
        )
        validate_no_access_stage_input(no_access)
        rendered = json.dumps(no_access, sort_keys=True)
        self.assertNotIn(SECRET, rendered)
        self.assertNotIn(self.path, rendered)
        self.assertNotIn("evidenceManifest", no_access)
        self.assertNotIn("verifiedChunkDigests", no_access)
        for digest in self.chunks:
            self.assertNotIn(digest, rendered)

        malicious = copy.deepcopy(no_access)
        malicious["rawSubmission"] = SECRET
        with self.assertRaisesRegex(MathFlowError, "unexpected fields"):
            validate_no_access_stage_input(malicious)

    def test_cross_bound_state_or_subject_is_rejected(self) -> None:
        bad_context = copy.deepcopy(self.context)
        bad_context["knowledgeStateDigest"] = "sha256:" + "f" * 64
        bad_context["contextDigest"] = "sha256:" + sha256_json(
            {key: value for key, value in bad_context.items() if key != "contextDigest"}
        )
        with self.assertRaisesRegex(MathFlowError, "different identity bindings"):
            build_no_access_stage_input(
                safe_facts=self.safe,
                impact_context=bad_context,
                research_state=self.state,
            )

    def test_with_access_binds_and_reconstructs_complete_manifested_submission(self) -> None:
        stage = build_with_access_stage_input(
            safe_facts=self.safe,
            impact_context=self.context,
            research_state=self.state,
            evidence_manifest=self.manifest,
            evidence_chunks=self.chunks,
        )
        validate_with_access_stage_input(stage)
        assembled = assemble_with_access_evidence(stage, self.chunks)
        self.assertEqual(
            {item["path"]: item["content"] for item in assembled}, self.files
        )
        self.assertEqual(stage["verifiedTotalBytes"], sum(map(len, self.files.values())))

        missing = dict(self.chunks)
        missing.pop(next(iter(missing)))
        with self.assertRaises(MathFlowError):
            assemble_with_access_evidence(stage, missing)

    def test_protocol_schemas_are_valid_json_and_structurally_closed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        names = [
            "submission-evidence-manifest-v1.schema.json",
            "counterfactual-safe-facts-v1.schema.json",
            "work-impact-context-v1.schema.json",
            "no-access-stage-input-v1.schema.json",
            "with-access-stage-input-v1.schema.json",
        ]
        for name in names:
            schema = json.loads((root / "protocol" / "schemas" / name).read_text())
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertFalse(schema["additionalProperties"], name)
        no_access_schema = json.loads(
            (root / "protocol" / "schemas" / names[3]).read_text()
        )
        top_level = no_access_schema["properties"]
        self.assertNotIn("evidenceManifest", top_level)
        self.assertNotIn("verifiedChunkDigests", top_level)
        self.assertNotIn("rawSubmission", top_level)


if __name__ == "__main__":
    unittest.main()
