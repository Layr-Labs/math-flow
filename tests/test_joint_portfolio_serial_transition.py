from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_serial_transition import (
    joint_portfolio_serial_response_schema_v1,
    make_joint_portfolio_semantic_packet_v1,
    reduce_joint_portfolio_serial_transition_v1,
)
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v10 import (
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_route_context,
)
from math_flow.work_accounting import (
    make_zero_work_accounting_state,
    validate_root_contract,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "protocol/experiments/joint-portfolio-serial-transition-v1"
ROOT_CONTRACT_PATH = (
    ROOT
    / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v2/root-contract-v2.json"
)


def accepted(claim_key: str, dependencies: list[str]) -> list[dict[str, object]]:
    return [
        {
            "claimKey": claim_key,
            "declaredStatement": f"The exact {claim_key} statement.",
            "validitySummary": f"The restricted {claim_key} statement is accepted.",
            "scopeQualifications": ["Only the stated scalar work package is resolved."],
            "evidenceTransactionIds": sorted(dependencies),
            "dependencyTransactionIds": sorted(dependencies),
        }
    ]


def boundary(program_id: str) -> dict[str, object]:
    return {
        "programId": program_id,
        "directResidualWorkScope": f"Residual technical work assigned only to {program_id}.",
        "activationCondition": f"Pursue {program_id} when its local route is selected.",
        "stoppingCondition": f"Stop {program_id} when its stated local objective is resolved.",
        "independentVariationRationale": "This package can be activated, stopped, or re-estimated independently of sibling routes.",
    }


ROOT_BOUNDARY = {
    "directResidualWorkScope": "Uninstantiated alternatives, root integration, and final certification not assigned to children.",
    "activationCondition": "The canonical exact-capacity objective remains unresolved.",
    "stoppingCondition": "The exact terminal condition in the root contract is met.",
    "independentVariationRationale": "Root residual excludes represented child work and contains only genuine integration and uninstantiated alternatives.",
}


class JointPortfolioSerialTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = json.loads((EXPERIMENT / "scenario-v1.json").read_text(encoding="utf-8"))
        self.problem = fixture["problemId"]
        self.tx1 = fixture["subjects"]["k1"]
        self.tx2 = fixture["subjects"]["k2"]
        self.tx3 = fixture["subjects"]["k3"]
        self.program1 = fixture["programIds"]["k1"]
        self.program2 = fixture["programIds"]["k2"]
        self.result1 = fixture["resultIds"]["k1"]
        self.result2 = fixture["resultIds"]["k2"]
        self.contract = validate_root_contract(
            json.loads(ROOT_CONTRACT_PATH.read_text(encoding="utf-8")), self.problem
        )
        self.origin = empty_research_program_state_v3(self.problem)
        self.accounting_origin = make_zero_work_accounting_state(
            root_contract=self.contract, knowledge_state=self.origin
        )

    def evidence(self, subject: str) -> dict[str, str]:
        path = f"problems/{self.problem}/contributions/{subject}/README.md"
        return {path: sha256_bytes(f"evidence:{subject}".encode())}

    def semantic_change(
        self,
        *,
        action: str,
        result_id: str,
        base_digest: str | None,
        claim_key: str,
        evidence_path: str,
        title: str,
        statement: str,
        dependencies: list[str],
        proof: str,
    ) -> dict[str, object]:
        return {
            "action": action,
            "id": result_id,
            "baseDigest": base_digest,
            "title": title,
            "statement": statement,
            "scopeQualifications": [
                "Only the stated scalar work package is resolved."
            ],
            "supportAdditions": {
                "proofs": [proof],
                "methods": [],
                "computations": [],
                "tools": [],
                "artifactPaths": [evidence_path],
                "attestationRefs": [],
            },
            "dependencyResultIds": sorted(dependencies),
            "claimKeys": [claim_key],
            "status": "active",
            "supersededByResultIds": [],
        }

    def authoring_packet(
        self,
        *,
        state: dict[str, object],
        claims: list[dict[str, object]],
        write_programs: list[str],
        write_results: list[str],
        create_programs: list[str],
        create_results: list[str],
    ) -> dict[str, object]:
        context = build_research_builder_v10_route_context(state, claims)
        route = {
            "schemaVersion": 1,
            "baseStateDigest": state["stateDigest"],
            "routeContextDigest": context["contextDigest"],
            "inspectProgramIds": [],
            "inspectResultIds": [],
            "searchQueries": [],
            "writeProgramIds": sorted(write_programs),
            "writeResultIds": sorted(write_results),
            "createProgramIds": sorted(create_programs),
            "createResultIds": sorted(create_results),
        }
        return build_research_builder_v10_authoring_packet(
            state,
            claims,
            route,
            route_context=context,
            max_programs=16,
            max_results=16,
        )

    def assessment(
        self,
        program_id: str,
        direct: str,
        incidence: str | None,
        claim_key: str,
    ) -> dict[str, object]:
        return {
            "programId": program_id,
            "directWorkHours": direct,
            "conditionalIncidence": incidence,
            "rationale": f"The accepted {claim_key} result fixes the live residual estimate for {program_id}.",
            "evidenceRefs": [claim_key],
        }

    def response(
        self,
        *,
        state: dict[str, object],
        accounting: dict[str, object],
        semantic: dict[str, object],
        scope: dict[str, object],
        program_changes: list[dict[str, object]],
        result_id: str,
        primary_program_id: str,
        assessments: list[dict[str, object]],
        topology_rationale: str | None,
    ) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "subjectTransactionId": semantic["subjectTransactionId"],
            "baseStateDigest": state["stateDigest"],
            "baseAccountingStateDigest": accounting["stateDigest"],
            "semanticPacketDigest": semantic["packetDigest"],
            "authoringPacketDigest": scope["authoringPacketDigest"],
            "programChanges": sorted(program_changes, key=lambda item: item["programId"]),
            "resultPlacements": [
                {
                    "resultId": result_id,
                    "primaryProgramId": primary_program_id,
                    "relatedProgramIds": [],
                }
            ],
            "programBoundaries": sorted(
                [boundary(str(item["programId"])) for item in program_changes],
                key=lambda item: item["programId"],
            ),
            "rootBoundary": copy.deepcopy(ROOT_BOUNDARY),
            "withAccessAssessments": sorted(
                assessments, key=lambda item: item["programId"]
            ),
            "topologyRationale": topology_rationale,
        }

    def reduce(
        self,
        *,
        response: dict[str, object],
        state: dict[str, object],
        accounting: dict[str, object],
        semantic: dict[str, object],
        scope: dict[str, object],
        claims: list[dict[str, object]],
        judgment: str,
        evidence: dict[str, str],
    ) -> dict[str, object]:
        return reduce_joint_portfolio_serial_transition_v1(
            response,
            base_state=state,
            base_accounting_state=accounting,
            root_contract=self.contract,
            semantic_packet=semantic,
            authoring_packet=scope,
            accepted_claims=claims,
            judgment_id=judgment,
            evidence_file_refs=evidence,
        )

    def k1(self) -> tuple[dict[str, object], dict[str, object]]:
        claim_key = f"{self.problem}/k1-code-induced-structure"
        claims = accepted(claim_key, [])
        evidence = self.evidence(self.tx1)
        path = next(iter(evidence))
        semantic = make_joint_portfolio_semantic_packet_v1(
            problem_id=self.problem,
            subject_transaction_id=self.tx1,
            base_state_digest=self.origin["stateDigest"],
            accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={
                "currentStateSummary": "The exact finite-block code-induced structural result is accepted; the canonical problem remains open.",
                "localResidualSummary": "Coordinate the code-induced route with independent converse and achievability work.",
            },
            result_changes=[
                self.semantic_change(
                    action="create",
                    result_id=self.result1,
                    base_digest=None,
                    claim_key=claim_key,
                    evidence_path=path,
                    title="Finite-block code-induced dependence balance",
                    statement="Every admissible code induces the stated finite-block structural identity.",
                    dependencies=[],
                    proof="An exact finite-block telescope proves the structural identity.",
                )
            ],
        )
        scope = self.authoring_packet(
            state=self.origin,
            claims=claims,
            write_programs=["root"],
            write_results=[],
            create_programs=[self.program1],
            create_results=[self.result1],
        )
        program = {
            "action": "create",
            "programId": self.program1,
            "baseDigest": None,
            "parentId": "root",
            "title": "Develop the code-induced converse route",
            "objective": "Turn exact code-induced structure into a certified converse.",
            "currentStateSummary": "The finite-block structural identity is established.",
            "localResidualSummary": "A useful reduction and channel-specific refinement remain open.",
            "status": "active",
        }
        response = self.response(
            state=self.origin,
            accounting=self.accounting_origin,
            semantic=semantic,
            scope=scope,
            program_changes=[program],
            result_id=self.result1,
            primary_program_id=self.program1,
            assessments=[
                self.assessment(self.program1, "200", "0.5", claim_key),
                self.assessment("root", "1000", None, claim_key),
            ],
            topology_rationale="The code-induced route is one durable result-owning root-child package.",
        )
        result = self.reduce(
            response=response,
            state=self.origin,
            accounting=self.accounting_origin,
            semantic=semantic,
            scope=scope,
            claims=claims,
            judgment="sha256:" + "1" * 64,
            evidence=evidence,
        )
        return result, {"claims": claims, "evidence": evidence, "semantic": semantic, "scope": scope, "response": response}

    def k2(
        self, k1: dict[str, object]
    ) -> tuple[dict[str, object], dict[str, object]]:
        state = k1["postState"]
        accounting = k1["withAccessState"]
        claim_key = f"{self.problem}/k2-uv-product-additivity"
        claims = accepted(claim_key, [self.tx1])
        evidence = self.evidence(self.tx2)
        path = next(iter(evidence))
        semantic = make_joint_portfolio_semantic_packet_v1(
            problem_id=self.problem,
            subject_transaction_id=self.tx2,
            base_state_digest=state["stateDigest"],
            accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={
                "currentStateSummary": "The UV scalar product-additivity theorem is accepted alongside the independent code-induced route.",
                "localResidualSummary": "The exact capacity problem still requires alternative converse, achievability, integration, and certification work.",
            },
            result_changes=[
                self.semantic_change(
                    action="create",
                    result_id=self.result2,
                    base_digest=None,
                    claim_key=claim_key,
                    evidence_path=path,
                    title="Exact product additivity of the averaged relaxed-UV scalar",
                    statement="The averaged separately relaxed UV scalar is exactly additive on finite products.",
                    dependencies=[self.result1],
                    proof="A chain-rule cancellation proves exact finite-product additivity.",
                )
            ],
        )
        scope = self.authoring_packet(
            state=state,
            claims=claims,
            write_programs=["root"],
            write_results=[],
            create_programs=[self.program2],
            create_results=[self.result2],
        )
        program = {
            "action": "create",
            "programId": self.program2,
            "baseDigest": None,
            "parentId": "root",
            "title": "Resolve blocking for the relaxed UV scalar",
            "objective": "Determine whether finite blocking strengthens the separately relaxed UV scalar.",
            "currentStateSummary": "Exact product additivity resolves the stated blocking question.",
            "localResidualSummary": "The stated package is complete; coupled UV systems are separate work.",
            "status": "active",
        }
        response = self.response(
            state=state,
            accounting=accounting,
            semantic=semantic,
            scope=scope,
            program_changes=[program],
            result_id=self.result2,
            primary_program_id=self.program2,
            assessments=[
                self.assessment(self.program2, "0", "1", claim_key),
                self.assessment("root", "900", None, claim_key),
            ],
            topology_rationale="The UV route is an independent root child: its mathematical use of K1 does not make its pursuit conditional on K1.",
        )
        result = self.reduce(
            response=response,
            state=state,
            accounting=accounting,
            semantic=semantic,
            scope=scope,
            claims=claims,
            judgment="sha256:" + "2" * 64,
            evidence=evidence,
        )
        return result, {"claims": claims, "evidence": evidence, "semantic": semantic, "scope": scope, "response": response}

    def k3(
        self, k2: dict[str, object]
    ) -> tuple[dict[str, object], dict[str, object]]:
        state = k2["postState"]
        accounting = k2["withAccessState"]
        claim_key = f"{self.problem}/k3-uv-independent-verification"
        claims = accepted(claim_key, [self.tx2])
        evidence = self.evidence(self.tx3)
        path = next(iter(evidence))
        prior = state["intermediateResults"][self.result2]
        semantic = make_joint_portfolio_semantic_packet_v1(
            problem_id=self.problem,
            subject_transaction_id=self.tx3,
            base_state_digest=state["stateDigest"],
            accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={
                "currentStateSummary": "Independent accepted evidence now supports the existing UV product-additivity result; no new route is created.",
                "localResidualSummary": "The exact capacity problem remains open with the same independent code-induced and UV work packages.",
            },
            result_changes=[
                self.semantic_change(
                    action="refresh",
                    result_id=self.result2,
                    base_digest=prior["digest"],
                    claim_key=claim_key,
                    evidence_path=path,
                    title=prior["title"],
                    statement="The averaged separately relaxed UV scalar is exactly additive on finite products, now with independent accepted verification.",
                    dependencies=[self.result1],
                    proof="An independent exact derivation verifies the same product-additivity theorem.",
                )
            ],
        )
        scope = self.authoring_packet(
            state=state,
            claims=claims,
            write_programs=["root", self.program2],
            write_results=[self.result2],
            create_programs=[],
            create_results=[],
        )
        prior_program = state["programs"][self.program2]
        program = {
            "action": "refresh",
            "programId": self.program2,
            "baseDigest": prior_program["digest"],
            "parentId": prior_program["parentId"],
            "title": prior_program["title"],
            "objective": prior_program["objective"],
            "currentStateSummary": "Exact product additivity remains established and now has independent accepted verification.",
            "localResidualSummary": prior_program["localResidualSummary"],
            "status": "active",
        }
        response = self.response(
            state=state,
            accounting=accounting,
            semantic=semantic,
            scope=scope,
            program_changes=[program],
            result_id=self.result2,
            primary_program_id=self.program2,
            assessments=[
                self.assessment(self.program2, "0", "1", claim_key),
                self.assessment("root", "850", None, claim_key),
            ],
            topology_rationale=None,
        )
        result = self.reduce(
            response=response,
            state=state,
            accounting=accounting,
            semantic=semantic,
            scope=scope,
            claims=claims,
            judgment="sha256:" + "3" * 64,
            evidence=evidence,
        )
        return result, {"claims": claims, "evidence": evidence, "semantic": semantic, "scope": scope, "response": response}

    def test_k1_k2_k3_create_independent_route_then_reuse_exact_ids(self) -> None:
        k1, _ = self.k1()
        k2, _ = self.k2(k1)
        before_k3_program_ids = set(k2["postState"]["programs"])
        before_k3_result_ids = set(k2["postState"]["intermediateResults"])
        k3, _ = self.k3(k2)

        self.assertEqual(k1["postState"]["programs"][self.program1]["parentId"], "root")
        self.assertEqual(k2["postState"]["programs"][self.program2]["parentId"], "root")
        self.assertEqual(set(k3["postState"]["programs"]), before_k3_program_ids)
        self.assertEqual(set(k3["postState"]["intermediateResults"]), before_k3_result_ids)
        self.assertEqual(k3["transition"]["topologyOperations"], [])
        refreshed = k3["postState"]["intermediateResults"][self.result2]
        self.assertEqual(
            refreshed["sourceTransactionIds"], [self.tx2, self.tx3]
        )
        self.assertEqual(
            [row["transactionId"] for row in refreshed["claimRefs"]],
            [self.tx2, self.tx3],
        )
        self.assertEqual(k1["withAccessState"]["totalWorkHours"], "1100")
        self.assertEqual(k2["withAccessState"]["totalWorkHours"], "1000")
        self.assertEqual(k3["withAccessState"]["totalWorkHours"], "950")

        k1_annotation = {
            row["nodeRef"]["id"]: row for row in k1["withAccessState"]["annotations"]
        }[self.program1]
        k2_annotation = {
            row["nodeRef"]["id"]: row for row in k2["withAccessState"]["annotations"]
        }[self.program1]
        self.assertEqual(k1_annotation, k2_annotation)

    def test_provider_schema_binds_every_authoritative_input_digest(self) -> None:
        k1, inputs = self.k1()
        schema = joint_portfolio_serial_response_schema_v1(
            subject_transaction_id=self.tx1,
            base_state_digest=self.origin["stateDigest"],
            base_accounting_state_digest=self.accounting_origin["stateDigest"],
            semantic_packet_digest=inputs["semantic"]["packetDigest"],
            authoring_packet_digest=inputs["scope"]["authoringPacketDigest"],
        )
        properties = schema["properties"]
        self.assertEqual(properties["subjectTransactionId"]["const"], self.tx1)
        self.assertEqual(properties["baseStateDigest"]["const"], self.origin["stateDigest"])
        self.assertEqual(
            properties["baseAccountingStateDigest"]["const"],
            self.accounting_origin["stateDigest"],
        )
        self.assertEqual(
            properties["semanticPacketDigest"]["const"],
            inputs["semantic"]["packetDigest"],
        )
        self.assertEqual(
            properties["authoringPacketDigest"]["const"],
            inputs["scope"]["authoringPacketDigest"],
        )
        self.assertEqual(k1["implementation"], "joint-portfolio-serial-transition-v1")

    def test_stale_response_binding_fails_before_reduction(self) -> None:
        _, inputs = self.k1()
        response = copy.deepcopy(inputs["response"])
        response["baseStateDigest"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(MathFlowError, "stale baseStateDigest"):
            self.reduce(
                response=response,
                state=self.origin,
                accounting=self.accounting_origin,
                semantic=inputs["semantic"],
                scope=inputs["scope"],
                claims=inputs["claims"],
                judgment="sha256:" + "1" * 64,
                evidence=inputs["evidence"],
            )

    def test_rehashed_evidence_substitution_fails_semantic_binding(self) -> None:
        _, inputs = self.k1()
        substituted = {
            path: "sha256:" + "e" * 64 for path in inputs["evidence"]
        }
        with self.assertRaisesRegex(MathFlowError, "evidence binding is stale"):
            self.reduce(
                response=inputs["response"],
                state=self.origin,
                accounting=self.accounting_origin,
                semantic=inputs["semantic"],
                scope=inputs["scope"],
                claims=inputs["claims"],
                judgment="sha256:" + "1" * 64,
                evidence=substituted,
            )

    def test_program_write_outside_local_scope_fails(self) -> None:
        k1, _ = self.k1()
        _, inputs = self.k2(k1)
        response = copy.deepcopy(inputs["response"])
        prior = k1["postState"]["programs"][self.program1]
        illicit = {
            "action": "refresh",
            "programId": self.program1,
            "baseDigest": prior["digest"],
            "parentId": prior["parentId"],
            "title": prior["title"],
            "objective": prior["objective"],
            "currentStateSummary": "Illicit out-of-scope refresh.",
            "localResidualSummary": prior["localResidualSummary"],
            "status": "active",
        }
        response["programChanges"] = sorted(
            [*response["programChanges"], illicit], key=lambda item: item["programId"]
        )
        response["programBoundaries"] = sorted(
            [*response["programBoundaries"], boundary(self.program1)],
            key=lambda item: item["programId"],
        )
        response["withAccessAssessments"] = sorted(
            [
                *response["withAccessAssessments"],
                self.assessment(
                    self.program1,
                    "200",
                    "0.5",
                    f"{self.problem}/k2-uv-product-additivity",
                ),
            ],
            key=lambda item: item["programId"],
        )
        with self.assertRaisesRegex(MathFlowError, "stale scope guard"):
            self.reduce(
                response=response,
                state=k1["postState"],
                accounting=k1["withAccessState"],
                semantic=inputs["semantic"],
                scope=inputs["scope"],
                claims=inputs["claims"],
                judgment="sha256:" + "2" * 64,
                evidence=inputs["evidence"],
            )

    def test_k3_cannot_replace_refresh_with_duplicate_result(self) -> None:
        k1, _ = self.k1()
        k2, _ = self.k2(k1)
        _, inputs = self.k3(k2)
        response = copy.deepcopy(inputs["response"])
        response["resultPlacements"][0]["resultId"] = "result-uv-duplicate"
        with self.assertRaisesRegex(MathFlowError, "place every semantic result"):
            self.reduce(
                response=response,
                state=k2["postState"],
                accounting=k2["withAccessState"],
                semantic=inputs["semantic"],
                scope=inputs["scope"],
                claims=inputs["claims"],
                judgment="sha256:" + "3" * 64,
                evidence=inputs["evidence"],
            )


if __name__ == "__main__":
    unittest.main()
