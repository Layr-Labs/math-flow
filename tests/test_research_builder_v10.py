from __future__ import annotations

import copy
import unittest

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v8 import apply_research_builder_v8_transition
from math_flow.research_builder_v10 import (
    apply_research_builder_v10_transition,
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_catalog,
    build_research_builder_v10_program_capsule,
    build_research_builder_v10_route_context,
    run_research_builder_v10_two_stage,
    search_research_builder_v10_catalog,
    validate_research_builder_v10_authoring_packet,
    validate_research_builder_v10_catalog,
)
from math_flow.repository import sha256_json


TX_A = "a" * 40
TX_B = "b" * 40
TX_D = "d" * 40
TX_C = "c" * 40
JUDGMENT_A = "sha256:" + "1" * 64
JUDGMENT_B = "sha256:" + "2" * 64
JUDGMENT_D = "sha256:" + "4" * 64
JUDGMENT_C = "sha256:" + "3" * 64
PATH_A = "problems/local-builder/contributions/a/README.md"
PATH_B = "problems/local-builder/contributions/b/README.md"
PATH_D = "problems/local-builder/contributions/d/README.md"
PATH_C = "problems/local-builder/contributions/c/README.md"
CONTENT_A = b"# Algebraic seed\n"
CONTENT_B = b"# Geometric extension\n"
CONTENT_D = b"# Remote spectral certificate\n"
CONTENT_C = b"# Strengthening\n"


def accepted(claim_key: str, dependencies: list[str] | None = None) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "declaredStatement": f"The exact {claim_key} statement.",
            "validitySummary": f"The restricted {claim_key} statement is established.",
            "scopeQualifications": ["Finite-dimensional scope."],
            "evidenceTransactionIds": [],
            "dependencyTransactionIds": sorted(dependencies or []),
        }
    ]


def without_digest(value: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(item) for key, item in value.items() if key != "digest"}


def add_result(
    base: dict[str, object],
    *,
    subject: str,
    judgment_id: str,
    claim_key: str,
    program_id: str,
    program_title: str,
    result_id: str,
    result_title: str,
    statement: str,
    path: str,
    content: bytes,
    dependency_transactions: list[str] | None = None,
    dependency_results: list[str] | None = None,
) -> dict[str, object]:
    root = without_digest(base["programs"]["root"])
    root["currentStateSummary"] = f"Accepted portfolio now includes {result_title}."
    root["sourceTransactionIds"] = sorted([*root["sourceTransactionIds"], subject])
    program = {
        "id": program_id,
        "parentId": "root",
        "title": program_title,
        "objective": f"Resolve the {program_title.lower()} objective.",
        "currentStateSummary": f"{result_title} is established.",
        "localResidualSummary": "The strongest local extension remains open.",
        "status": "active",
        "intermediateResultIds": [result_id],
        "sourceTransactionIds": [subject],
        "lineage": [],
    }
    result = {
        "id": result_id,
        "primaryProgramId": program_id,
        "relatedProgramIds": [],
        "title": result_title,
        "statement": statement,
        "scopeQualifications": ["Finite-dimensional scope."],
        "support": {
            "proofs": [f"Exact proof of {result_title}."],
            "methods": [],
            "computations": [],
            "tools": [],
            "artifactRefs": [{"path": path, "digest": sha256_bytes(content)}],
            "attestationRefs": [],
        },
        "dependencyResultIds": sorted(dependency_results or []),
        "claimRefs": [{"transactionId": subject, "claimKey": claim_key}],
        "sourceTransactionIds": [subject],
        "judgmentIds": [judgment_id],
        "status": "active",
        "supersededByResultIds": [],
    }
    transition = {
        "schemaVersion": 1,
        "subjectTransactionId": subject,
        "baseStateDigest": base["stateDigest"],
        "contentOperations": [
            {
                "entityKind": "program",
                "entityId": "root",
                "baseDigest": base["programs"]["root"]["digest"],
                "value": root,
            },
            {
                "entityKind": "program",
                "entityId": program_id,
                "baseDigest": None,
                "value": program,
            },
            {
                "entityKind": "intermediateResult",
                "entityId": result_id,
                "baseDigest": None,
                "value": result,
            },
        ],
        "topologyOperations": [],
        "contribution": {
            "claimKeys": [claim_key],
            "directProgramIds": [program_id],
            "intermediateResultIds": [result_id],
        },
        "placementAudit": {
            "basis": "local-objective",
            "rationale": "This is a durable local objective.",
            "relatedProgramIds": [program_id],
        },
        "topologyRationale": None,
    }
    return apply_research_builder_v8_transition(
        base,
        transition,
        accepted_claims=accepted(claim_key, dependency_transactions),
        judgment_id=judgment_id,
        evidence_file_refs={path: sha256_bytes(content)},
    )["postState"]


class ResearchBuilderV10Tests(unittest.TestCase):
    def setUp(self) -> None:
        state = empty_research_program_state_v3("local-builder")
        state = add_result(
            state,
            subject=TX_A,
            judgment_id=JUDGMENT_A,
            claim_key="claim-a",
            program_id="program/algebra",
            program_title="Algebraic reduction",
            result_id="result/algebra-seed",
            result_title="Algebraic seed lemma",
            statement="A finite algebraic reduction holds.",
            path=PATH_A,
            content=CONTENT_A,
        )
        state = add_result(
            state,
            subject=TX_B,
            judgment_id=JUDGMENT_B,
            claim_key="claim-b",
            program_id="program/geometry",
            program_title="Geometric extension",
            result_id="result/geometric-extension",
            result_title="Geometric extension theorem",
            statement="The geometric extension follows from the algebraic seed.",
            path=PATH_B,
            content=CONTENT_B,
            dependency_transactions=[TX_A],
            dependency_results=["result/algebra-seed"],
        )
        state = add_result(
            state,
            subject=TX_D,
            judgment_id=JUDGMENT_D,
            claim_key="claim-d",
            program_id="program/remote",
            program_title="Remote spectral method",
            result_id="result/remote-certificate",
            result_title="Remote spectral certificate",
            statement="A remote spectral certificate excludes the exceptional case.",
            path=PATH_D,
            content=CONTENT_D,
        )
        self.base = state
        self.claims = accepted("claim-c", [TX_B])
        self.route_context = build_research_builder_v10_route_context(
            self.base, self.claims, max_root_children=1, max_root_results=1
        )

    def route_plan(
        self,
        *,
        inspect_programs: list[str] | None = None,
        inspect_results: list[str] | None = None,
        searches: list[dict[str, object]] | None = None,
        write_programs: list[str] | None = None,
        write_results: list[str] | None = None,
        create_programs: list[str] | None = None,
        create_results: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "baseStateDigest": self.base["stateDigest"],
            "routeContextDigest": self.route_context["contextDigest"],
            "inspectProgramIds": inspect_programs or [],
            "inspectResultIds": inspect_results or [],
            "searchQueries": searches or [],
            "writeProgramIds": write_programs or [],
            "writeResultIds": write_results or [],
            "createProgramIds": create_programs or [],
            "createResultIds": create_results or [],
        }

    def strengthening_transition(self) -> dict[str, object]:
        root = without_digest(self.base["programs"]["root"])
        root["currentStateSummary"] = "The geometric extension is strengthened."
        root["sourceTransactionIds"] = sorted([*root["sourceTransactionIds"], TX_C])
        program = without_digest(self.base["programs"]["program/geometry"])
        program["currentStateSummary"] = "The strengthened geometric extension holds."
        program["sourceTransactionIds"] = sorted([*program["sourceTransactionIds"], TX_C])
        result = without_digest(self.base["intermediateResults"]["result/geometric-extension"])
        result["statement"] = "The strengthened geometric extension follows from the algebraic seed."
        result["claimRefs"] = sorted(
            [*result["claimRefs"], {"transactionId": TX_C, "claimKey": "claim-c"}],
            key=lambda item: (item["transactionId"], item["claimKey"]),
        )
        result["sourceTransactionIds"] = sorted([*result["sourceTransactionIds"], TX_C])
        result["judgmentIds"] = sorted([*result["judgmentIds"], JUDGMENT_C])
        result["support"]["proofs"] = sorted(
            [*result["support"]["proofs"], "Exact proof of the strengthening."]
        )
        result["support"]["artifactRefs"] = sorted(
            [
                *result["support"]["artifactRefs"],
                {"path": PATH_C, "digest": sha256_bytes(CONTENT_C)},
            ],
            key=lambda item: (item["path"], item["digest"]),
        )
        return {
            "schemaVersion": 1,
            "subjectTransactionId": TX_C,
            "baseStateDigest": self.base["stateDigest"],
            "contentOperations": [
                {"entityKind": "program", "entityId": "root", "baseDigest": self.base["programs"]["root"]["digest"], "value": root},
                {"entityKind": "program", "entityId": "program/geometry", "baseDigest": self.base["programs"]["program/geometry"]["digest"], "value": program},
                {"entityKind": "intermediateResult", "entityId": "result/geometric-extension", "baseDigest": self.base["intermediateResults"]["result/geometric-extension"]["digest"], "value": result},
            ],
            "topologyOperations": [],
            "contribution": {"claimKeys": ["claim-c"], "directProgramIds": ["program/geometry"], "intermediateResultIds": ["result/geometric-extension"]},
            "placementAudit": {"basis": "local-objective", "rationale": "This strengthens the same local objective.", "relatedProgramIds": ["program/geometry"]},
            "topologyRationale": None,
        }

    def packet(self) -> dict[str, object]:
        return build_research_builder_v10_authoring_packet(
            self.base,
            self.claims,
            self.route_plan(
                inspect_programs=["program/geometry"],
                inspect_results=["result/geometric-extension"],
                searches=[
                    {
                        "query": "remote spectral certificate",
                        "entityKinds": ["program", "intermediateResult"],
                        "limit": 2,
                    }
                ],
                write_programs=["root", "program/geometry"],
                write_results=["result/geometric-extension"],
            ),
            route_context=self.route_context,
        )

    def test_catalog_and_capsules_are_compact_paged_and_replay_bound(self) -> None:
        catalog = build_research_builder_v10_catalog(self.base)
        validate_research_builder_v10_catalog(catalog, base_state=self.base)
        rendered = str(catalog)
        self.assertNotIn("sourceTransactionIds", rendered)
        self.assertNotIn("claimRefs", rendered)
        self.assertNotIn("judgmentIds", rendered)
        self.assertNotIn("Exact proof", rendered)
        capsule = build_research_builder_v10_program_capsule(
            catalog, "root", max_children=1, max_results=1
        )
        self.assertEqual(capsule["childProgramCount"], 3)
        self.assertEqual(len(capsule["childPrograms"]), 1)
        self.assertEqual(capsule["nextChildProgramOffset"], 1)
        tampered = copy.deepcopy(catalog)
        tampered["programCards"]["root"]["title"] = "Injected"
        with self.assertRaisesRegex(MathFlowError, "digest mismatch"):
            validate_research_builder_v10_catalog(tampered)

    def test_global_lexical_search_finds_distant_branch(self) -> None:
        catalog = build_research_builder_v10_catalog(self.base)
        matches = search_research_builder_v10_catalog(
            catalog, "remote spectral certificate", limit=3
        )
        ids = [item["entityId"] for item in matches]
        self.assertIn("result/remote-certificate", ids)
        self.assertIn("program/remote", ids)

    def test_packet_loads_declared_dependency_closure_and_exact_local_records(self) -> None:
        packet = self.packet()
        validate_research_builder_v10_authoring_packet(
            packet, base_state=self.base, accepted_claims=self.claims
        )
        read_set = packet["readSet"]
        self.assertEqual(
            read_set["dependencyResultIds"],
            ["result/algebra-seed", "result/geometric-extension"],
        )
        self.assertIn("result/remote-certificate", read_set["searchResultIds"])
        self.assertIn("program/remote", read_set["programIds"])
        self.assertIn("root", read_set["programIds"])
        root_view = packet["programs"]["root"]
        self.assertNotIn("sourceTransactionIds", root_view)
        self.assertNotIn("intermediateResultIds", root_view)
        self.assertEqual(root_view["recordDigest"], self.base["programs"]["root"]["digest"])
        exact_result = packet["intermediateResults"]["result/geometric-extension"]
        self.assertNotIn("claimRefs", exact_result)
        self.assertNotIn("sourceTransactionIds", exact_result)
        self.assertNotIn("judgmentIds", exact_result)
        self.assertEqual(exact_result["claimRefCount"], 1)
        self.assertEqual(
            exact_result["claimRefsDigest"],
            "sha256:"
            + sha256_json(
                self.base["intermediateResults"]["result/geometric-extension"]["claimRefs"]
            ),
        )
        self.assertNotIn("support", exact_result)
        self.assertEqual(exact_result["supportCounts"]["proofs"], 1)
        self.assertEqual(
            exact_result["supportDigest"],
            "sha256:"
            + sha256_json(
                self.base["intermediateResults"]["result/geometric-extension"]["support"]
            ),
        )

    def test_packet_fails_instead_of_truncating_mandatory_closure(self) -> None:
        with self.assertRaisesRegex(MathFlowError, "dependency closure exceeds budget"):
            build_research_builder_v10_route_context(
                self.base,
                self.claims,
                max_dependency_results=1,
            )
        with self.assertRaisesRegex(MathFlowError, "result read-set exceeds budget"):
            build_research_builder_v10_authoring_packet(
                self.base,
                self.claims,
                self.route_plan(
                    write_programs=["root", "program/geometry"],
                    write_results=["result/geometric-extension"],
                ),
                route_context=self.route_context,
                max_results=1,
            )

    def test_scoped_apply_preserves_hidden_state(self) -> None:
        packet = self.packet()
        transition = self.strengthening_transition()
        hidden_program = copy.deepcopy(self.base["programs"]["program/remote"])
        hidden_result = copy.deepcopy(self.base["intermediateResults"]["result/remote-certificate"])
        reduced = apply_research_builder_v10_transition(
            self.base,
            transition,
            authoring_packet=packet,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT_C,
            evidence_file_refs={PATH_C: sha256_bytes(CONTENT_C)},
        )
        post = reduced["postState"]
        self.assertEqual(post["programs"]["program/remote"], hidden_program)
        self.assertEqual(post["intermediateResults"]["result/remote-certificate"], hidden_result)
        self.assertEqual(reduced["authoringPacketDigest"], packet["authoringPacketDigest"])

    def test_write_outside_scope_and_recomputed_packet_tampering_fail(self) -> None:
        packet = self.packet()
        transition = self.strengthening_transition()
        remote = without_digest(self.base["programs"]["program/remote"])
        remote["currentStateSummary"] = "Unauthorized rewrite."
        remote["sourceTransactionIds"] = sorted([*remote["sourceTransactionIds"], TX_C])
        transition["contentOperations"].append(
            {
                "entityKind": "program",
                "entityId": "program/remote",
                "baseDigest": self.base["programs"]["program/remote"]["digest"],
                "value": remote,
            }
        )
        with self.assertRaisesRegex(MathFlowError, "writes outside scope"):
            apply_research_builder_v10_transition(
                self.base,
                transition,
                authoring_packet=packet,
                accepted_claims=self.claims,
                judgment_id=JUDGMENT_C,
                evidence_file_refs={PATH_C: sha256_bytes(CONTENT_C)},
            )
        tampered = copy.deepcopy(packet)
        tampered["readSet"]["programIds"].remove("program/remote")
        core = {key: value for key, value in tampered.items() if key != "authoringPacketDigest"}
        tampered["authoringPacketDigest"] = "sha256:" + sha256_json(core)
        with self.assertRaisesRegex(MathFlowError, "not reducer-derived"):
            validate_research_builder_v10_authoring_packet(
                tampered, base_state=self.base, accepted_claims=self.claims
            )

    def test_two_stage_runner_uses_separate_fake_route_and_author_calls(self) -> None:
        calls: list[str] = []

        def router(context: dict[str, object]) -> dict[str, object]:
            calls.append("route")
            return {
                "schemaVersion": 1,
                "baseStateDigest": context["baseStateDigest"],
                "routeContextDigest": context["contextDigest"],
                "inspectProgramIds": ["program/geometry"],
                "inspectResultIds": ["result/geometric-extension"],
                "searchQueries": [],
                "writeProgramIds": ["root", "program/geometry"],
                "writeResultIds": ["result/geometric-extension"],
                "createProgramIds": [],
                "createResultIds": [],
            }

        def author(packet: dict[str, object]) -> dict[str, object]:
            calls.append("author")
            self.assertIn("result/algebra-seed", packet["intermediateResults"])
            return self.strengthening_transition()

        result = run_research_builder_v10_two_stage(
            base_state=self.base,
            accepted_claims=self.claims,
            judgment_id=JUDGMENT_C,
            evidence_file_refs={PATH_C: sha256_bytes(CONTENT_C)},
            router=router,
            author=author,
        )
        self.assertEqual(calls, ["route", "author"])
        self.assertEqual(result["reduced"]["postState"]["ledgerHead"], TX_C)


if __name__ == "__main__":
    unittest.main()
