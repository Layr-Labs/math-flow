from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_boundaries import make_joint_portfolio_boundary_state_v1
from math_flow.joint_portfolio_serial_transition_v2 import (
    _validate_evidence_refs,
    joint_portfolio_serial_response_schema_v2,
    make_joint_portfolio_semantic_packet_v2,
    reduce_joint_portfolio_serial_transition_v2,
)
from math_flow.repository import sha256_json
from math_flow.research_builder_v7 import empty_research_program_state_v3
from math_flow.research_builder_v7 import validate_research_program_state_v3
from math_flow.research_builder_v10 import (
    build_research_builder_v10_authoring_packet,
    build_research_builder_v10_route_context,
)
from math_flow.work_accounting import make_zero_work_accounting_state, validate_root_contract, validate_work_accounting_state


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k1-v2/root-contract-v2.json"
PROBLEM = "bssc-sum-capacity"
TX1, TX2, TX3 = "1" * 40, "2" * 40, "3" * 40
PROGRAM1 = "program-bssc-code-induced-converse"
PROGRAM2 = "program-bssc-uv-product-branchwise-additivity"
RESULT1 = "result-bssc-code-induced-finite-block-dependence-balance"
RESULT2A = "result-uv-average-product-additivity"
RESULT2B = "result-uv-branchwise-symmetry-specialization"


def accepted(claim: str, dependencies: list[str]) -> list[dict[str, object]]:
    return [{
        "claimKey": claim,
        "declaredStatement": f"Accepted statement for {claim}.",
        "validitySummary": f"The narrow claim {claim} is accepted.",
        "scopeQualifications": ["Only the stated work package is resolved."],
        "evidenceTransactionIds": sorted(dependencies),
        "dependencyTransactionIds": sorted(dependencies),
    }]


def boundary(program_id: str) -> dict[str, object]:
    return {
        "programId": program_id,
        "directResidualWorkScope": f"Direct residual work assigned only to {program_id}.",
        "activationCondition": f"Activate {program_id} when its local policy selects it.",
        "stoppingCondition": f"Stop {program_id} when its local objective is resolved or pruned.",
        "independentVariationRationale": f"The inclusion and stopping decision for {program_id} varies independently where represented.",
    }


class JointPortfolioSerialTransitionV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = validate_root_contract(json.loads(CONTRACT_PATH.read_text()), PROBLEM)
        self.origin = empty_research_program_state_v3(PROBLEM)
        self.accounting_origin = make_zero_work_accounting_state(root_contract=self.contract, knowledge_state=self.origin)
        self.boundary_origin = make_joint_portfolio_boundary_state_v1(
            knowledge_state=self.origin,
            boundaries=[boundary("root")],
        )

    def evidence(self, subject: str) -> dict[str, str]:
        path = f"problems/{PROBLEM}/contributions/{subject}/README.md"
        return {path: sha256_bytes(f"evidence:{subject}".encode())}

    def claims_ref(self, packet: dict[str, object], claim: str) -> list[dict[str, str]]:
        return [{"kind": "accepted-claim", "id": claim, "digest": str(packet["acceptedClaimsDigest"])}]

    def result_change(
        self,
        *,
        action: str,
        result_id: str,
        claim_keys: list[str],
        evidence_path: str,
        base: dict[str, object] | None = None,
        title: str | None = None,
        statement: str | None = None,
        qualifications: list[str] | None = None,
        dependencies: list[str] | None = None,
        status: str = "active",
        successors: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "action": action,
            "id": result_id,
            "baseDigest": base["digest"] if base else None,
            "title": title if title is not None else str(base["title"]),
            "statement": statement if statement is not None else str(base["statement"]),
            "scopeQualifications": qualifications if qualifications is not None else list(base["scopeQualifications"]),
            "supportAdditions": {
                "proofs": [f"Accepted support from {claim_keys[0]}."] if claim_keys else [],
                "methods": [], "computations": [], "tools": [],
                "artifactPaths": [evidence_path] if claim_keys else [],
                "attestationRefs": [],
            },
            "dependencyResultIds": sorted(dependencies if dependencies is not None else list(base["dependencyResultIds"])),
            "claimKeys": sorted(claim_keys),
            "status": status,
            "supersededByResultIds": sorted(successors if successors is not None else list(base["supersededByResultIds"] if base else [])),
        }

    def create_result(self, *, result_id: str, claim: str, path: str, title: str, statement: str, dependencies: list[str]) -> dict[str, object]:
        return self.result_change(
            action="create", result_id=result_id, claim_keys=[claim], evidence_path=path,
            title=title, statement=statement,
            qualifications=["Only the stated work package is resolved."],
            dependencies=dependencies, status="active", successors=[],
        )

    def scope(
        self,
        state: dict[str, object],
        claims: list[dict[str, object]],
        *,
        write_programs: list[str], write_results: list[str],
        create_programs: list[str], create_results: list[str],
        inspect_programs: list[str] | None = None,
    ) -> dict[str, object]:
        context = build_research_builder_v10_route_context(state, claims)
        route = {
            "schemaVersion": 1, "baseStateDigest": state["stateDigest"],
            "routeContextDigest": context["contextDigest"],
            "inspectProgramIds": sorted(inspect_programs or []), "inspectResultIds": [],
            "searchQueries": [], "writeProgramIds": sorted(write_programs),
            "writeResultIds": sorted(write_results), "createProgramIds": sorted(create_programs),
            "createResultIds": sorted(create_results),
        }
        return build_research_builder_v10_authoring_packet(
            state, claims, route, route_context=context, max_programs=24, max_results=24,
        )

    def assessment(self, program: str, direct: str, incidence: str | None, packet: dict[str, object], claim: str) -> dict[str, object]:
        return {
            "programId": program, "directWorkHours": direct,
            "conditionalIncidence": incidence,
            "rationale": f"The sealed accepted claim updates d/P for {program}.",
            "evidenceRefs": self.claims_ref(packet, claim),
        }

    def response(
        self, *, state: dict[str, object], accounting: dict[str, object],
        boundary_state: dict[str, object], packet: dict[str, object], scope: dict[str, object],
        programs: list[dict[str, object]], placements: list[dict[str, object]],
        affected: list[str], assessments: list[dict[str, object]], rationale: str | None,
    ) -> dict[str, object]:
        return {
            "schemaVersion": 2, "subjectTransactionId": packet["subjectTransactionId"],
            "baseStateDigest": state["stateDigest"], "baseAccountingStateDigest": accounting["stateDigest"],
            "baseBoundaryStateDigest": boundary_state["stateDigest"],
            "semanticPacketDigest": packet["packetDigest"], "authoringPacketDigest": scope["authoringPacketDigest"],
            "programChanges": sorted(programs, key=lambda row: row["programId"]),
            "resultPlacements": sorted(placements, key=lambda row: row["resultId"]),
            "programBoundaries": [boundary(program) for program in sorted(affected)],
            "withAccessAssessments": sorted(assessments, key=lambda row: row["programId"]),
            "topologyRationale": rationale,
        }

    def reduce(self, inputs: dict[str, object]) -> dict[str, object]:
        return reduce_joint_portfolio_serial_transition_v2(
            inputs["response"], base_state=inputs["state"],
            base_accounting_state=inputs["accounting"], base_boundary_state=inputs["boundaries"],
            root_contract=self.contract, semantic_packet=inputs["packet"], authoring_packet=inputs["scope"],
            accepted_claims=inputs["claims"], judgment_id=inputs["judgment"],
            evidence_file_refs=inputs["evidence"],
        )

    def k1(self) -> tuple[dict[str, object], dict[str, object]]:
        claim = f"{PROBLEM}/k1-code-induced"
        claims, evidence = accepted(claim, []), self.evidence(TX1)
        path = next(iter(evidence))
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX1, base_state_digest=self.origin["stateDigest"],
            accepted_claims=claims, evidence_file_refs=evidence,
            root_update={"currentStateSummary": "The K1 structural theorem is accepted.", "localResidualSummary": "The canonical problem remains open."},
            result_changes=[self.create_result(result_id=RESULT1, claim=claim, path=path, title="Finite-block structural theorem", statement="Every code induces the exact finite-block balance.", dependencies=[])],
        )
        scope = self.scope(self.origin, claims, write_programs=["root"], write_results=[], create_programs=[PROGRAM1], create_results=[RESULT1])
        program = {"action": "create", "programId": PROGRAM1, "baseDigest": None, "parentId": "root", "title": "Code-induced converse", "objective": "Develop the code-induced route.", "currentStateSummary": "The structural theorem is established.", "localResidualSummary": "Refinement remains.", "status": "active"}
        response = self.response(
            state=self.origin, accounting=self.accounting_origin, boundary_state=self.boundary_origin,
            packet=packet, scope=scope, programs=[program],
            placements=[{"resultId": RESULT1, "primaryProgramId": PROGRAM1, "relatedProgramIds": []}],
            affected=["root", PROGRAM1],
            assessments=[self.assessment(PROGRAM1, "200", "0.5", packet, claim), self.assessment("root", "1000", None, packet, claim)],
            rationale="One durable K1 work package is created.",
        )
        inputs = {"state": self.origin, "accounting": self.accounting_origin, "boundaries": self.boundary_origin, "packet": packet, "scope": scope, "claims": claims, "evidence": evidence, "judgment": "sha256:" + "1" * 64, "response": response}
        return self.reduce(inputs), inputs

    def k2(self, k1: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
        state, accounting, boundaries = k1["postState"], k1["withAccessState"], k1["boundaryState"]
        claim = f"{PROBLEM}/k2-uv-chain"
        claims, evidence = accepted(claim, [TX1]), self.evidence(TX2)
        path = next(iter(evidence))
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX2, base_state_digest=state["stateDigest"],
            accepted_claims=claims, evidence_file_refs=evidence,
            root_update={"currentStateSummary": "The two-result UV theorem chain is accepted alongside K1.", "localResidualSummary": "Other capacity work remains."},
            result_changes=[
                self.create_result(result_id=RESULT2A, claim=claim, path=path, title="UV average product additivity", statement="The separately relaxed averaged UV scalar is product additive.", dependencies=[]),
                self.create_result(result_id=RESULT2B, claim=claim, path=path, title="UV symmetry specialization", statement="Receiver-skew symmetry gives the exact branchwise BSSC specialization.", dependencies=[RESULT1, RESULT2A]),
            ],
        )
        scope = self.scope(state, claims, write_programs=["root"], write_results=[], create_programs=[PROGRAM2], create_results=[RESULT2A, RESULT2B])
        program = {"action": "create", "programId": PROGRAM2, "baseDigest": None, "parentId": "root", "title": "Relaxed UV scalar tensorization", "objective": "Resolve blocking for the separately relaxed UV scalars.", "currentStateSummary": "The two-result theorem chain resolves the package.", "localResidualSummary": "No residual remains in the narrow package.", "status": "active"}
        response = self.response(
            state=state, accounting=accounting, boundary_state=boundaries, packet=packet, scope=scope,
            programs=[program], placements=[
                {"resultId": RESULT2A, "primaryProgramId": PROGRAM2, "relatedProgramIds": []},
                {"resultId": RESULT2B, "primaryProgramId": PROGRAM2, "relatedProgramIds": []},
            ], affected=["root", PROGRAM2],
            assessments=[self.assessment(PROGRAM2, "0", "1", packet, claim), self.assessment("root", "900", None, packet, claim)],
            rationale="The two results share one stopping policy in one independent root-child route.",
        )
        inputs = {"state": state, "accounting": accounting, "boundaries": boundaries, "packet": packet, "scope": scope, "claims": claims, "evidence": evidence, "judgment": "sha256:" + "2" * 64, "response": response}
        return self.reduce(inputs), inputs

    def k3(self, k2: dict[str, object], *, completed: bool = False) -> tuple[dict[str, object], dict[str, object]]:
        state, accounting, boundaries = k2["postState"], k2["withAccessState"], k2["boundaryState"]
        claim = f"{PROBLEM}/k3-uv-verification"
        claims, evidence = accepted(claim, [TX2]), self.evidence(TX3)
        path = next(iter(evidence))
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX3, base_state_digest=state["stateDigest"], accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={"currentStateSummary": "K3 adds accepted support to both exact K2 UV results.", "localResidualSummary": "The topology and narrow package remain stable."},
            result_changes=[
                self.result_change(action="support", result_id=result_id, claim_keys=[claim], evidence_path=path, base=state["intermediateResults"][result_id])
                for result_id in (RESULT2A, RESULT2B)
            ],
        )
        scope = self.scope(state, claims, write_programs=["root", PROGRAM2], write_results=[RESULT2A, RESULT2B], create_programs=[], create_results=[])
        prior = state["programs"][PROGRAM2]
        program = {"action": "refresh", "programId": PROGRAM2, "baseDigest": prior["digest"], "parentId": prior["parentId"], "title": prior["title"], "objective": prior["objective"], "currentStateSummary": "The exact two-result chain now has independent accepted support.", "localResidualSummary": prior["localResidualSummary"], "status": "completed" if completed else prior["status"]}
        response = self.response(
            state=state, accounting=accounting, boundary_state=boundaries, packet=packet, scope=scope,
            programs=[program], placements=[
                {"resultId": result_id, "primaryProgramId": PROGRAM2, "relatedProgramIds": []}
                for result_id in (RESULT2A, RESULT2B)
            ], affected=["root", PROGRAM2],
            assessments=[self.assessment(PROGRAM2, "0", "0" if completed else "1", packet, claim), self.assessment("root", "850", None, packet, claim)],
            rationale=(
                "The accepted support closes the represented work package."
                if completed
                else None
            ),
        )
        inputs = {"state": state, "accounting": accounting, "boundaries": boundaries, "packet": packet, "scope": scope, "claims": claims, "evidence": evidence, "judgment": "sha256:" + "3" * 64, "response": response}
        return self.reduce(inputs), inputs

    def test_k1_k2_two_results_and_k3_support_only_reuse(self) -> None:
        k1, _ = self.k1()
        k2, _ = self.k2(k1)
        before_programs = set(k2["postState"]["programs"])
        before_results = set(k2["postState"]["intermediateResults"])
        k3, _ = self.k3(k2)
        self.assertEqual(set(k3["postState"]["programs"]), before_programs)
        self.assertEqual(set(k3["postState"]["intermediateResults"]), before_results)
        self.assertEqual(k3["transition"]["topologyOperations"], [])
        for result_id in (RESULT2A, RESULT2B):
            before = k2["postState"]["intermediateResults"][result_id]
            after = k3["postState"]["intermediateResults"][result_id]
            for field in ("title", "statement", "scopeQualifications", "dependencyResultIds", "primaryProgramId", "relatedProgramIds"):
                self.assertEqual(after[field], before[field])
            self.assertEqual(after["sourceTransactionIds"], [TX2, TX3])
        self.assertEqual(k3["accountingAffectedProgramIds"], [PROGRAM2, "root"])
        before_annotations = {
            row["nodeRef"]["id"]: row
            for row in k2["withAccessState"]["annotations"]
        }
        after_annotations = {
            row["nodeRef"]["id"]: row
            for row in k3["withAccessState"]["annotations"]
        }
        self.assertEqual(after_annotations[PROGRAM1], before_annotations[PROGRAM1])

    def test_cumulative_boundaries_carry_unaffected_programs_exactly(self) -> None:
        k1, _ = self.k1()
        k2, _ = self.k2(k1)
        k3, _ = self.k3(k2)

        def rows(state: dict[str, object]) -> dict[str, dict[str, object]]:
            return {
                row["programId"]: row
                for row in state["boundaryState"]["boundaries"]
            }

        k1_rows, k2_rows, k3_rows = rows(k1), rows(k2), rows(k3)
        self.assertEqual(k2_rows[PROGRAM1], k1_rows[PROGRAM1])
        self.assertEqual(k3_rows[PROGRAM1], k2_rows[PROGRAM1])
        self.assertEqual(set(k3_rows), set(k3["postState"]["programs"]))
        self.assertEqual(
            k3["boundaryState"]["knowledgeStateDigest"],
            k3["postState"]["stateDigest"],
        )

    def test_support_refresh_cannot_silently_replace_semantics(self) -> None:
        k1, _ = self.k1(); k2, _ = self.k2(k1); _, inputs = self.k3(k2)
        packet = copy.deepcopy(inputs["packet"])
        packet["resultChanges"][0]["statement"] += " Stronger claim."
        core = {key: value for key, value in packet.items() if key != "packetDigest"}
        packet["packetDigest"] = f"sha256:{sha256_json(core)}"
        inputs = {**inputs, "packet": packet}
        with self.assertRaisesRegex(MathFlowError, "cannot replace result semantics"):
            self.reduce(inputs)

    def test_child_insertion_requires_parent_wplus_reassessment(self) -> None:
        k1, _ = self.k1(); _, inputs = self.k2(k1)
        inputs = copy.deepcopy(inputs)
        inputs["scope"] = self.scope(
            inputs["state"], inputs["claims"],
            write_programs=["root", PROGRAM1], write_results=[],
            create_programs=[PROGRAM2], create_results=[RESULT2A, RESULT2B],
        )
        inputs["response"]["authoringPacketDigest"] = inputs["scope"]["authoringPacketDigest"]
        inputs["response"]["programChanges"][0]["parentId"] = PROGRAM1
        with self.assertRaisesRegex(MathFlowError, "boundaries must cover every accounting-affected"):
            self.reduce(inputs)

    def test_root_owned_result_is_canonical(self) -> None:
        claim = f"{PROBLEM}/root-integration-result"
        claims, evidence = accepted(claim, []), self.evidence(TX1)
        path = next(iter(evidence))
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX1, base_state_digest=self.origin["stateDigest"], accepted_claims=claims, evidence_file_refs=evidence,
            root_update={"currentStateSummary": "A root-owned integration result is accepted.", "localResidualSummary": "Further integration remains."},
            result_changes=[self.create_result(result_id="result-root-integration", claim=claim, path=path, title="Root integration lemma", statement="The integration condition holds.", dependencies=[])],
        )
        scope = self.scope(self.origin, claims, write_programs=["root"], write_results=[], create_programs=[], create_results=["result-root-integration"])
        response = self.response(
            state=self.origin, accounting=self.accounting_origin, boundary_state=self.boundary_origin, packet=packet, scope=scope,
            programs=[], placements=[{"resultId": "result-root-integration", "primaryProgramId": "root", "relatedProgramIds": []}], affected=["root"],
            assessments=[self.assessment("root", "100", None, packet, claim)], rationale="The result belongs to root integration rather than a fabricated child.",
        )
        reduced = self.reduce({"state": self.origin, "accounting": self.accounting_origin, "boundaries": self.boundary_origin, "packet": packet, "scope": scope, "claims": claims, "evidence": evidence, "judgment": "sha256:" + "1" * 64, "response": response})
        self.assertEqual(reduced["postState"]["intermediateResults"]["result-root-integration"]["primaryProgramId"], "root")

    def test_shared_result_has_one_identity_and_all_accounting_owners(self) -> None:
        k1, _ = self.k1()
        k2, _ = self.k2(k1)
        state, accounting, boundaries = k2["postState"], k2["withAccessState"], k2["boundaryState"]
        claim = f"{PROBLEM}/shared-root-route-interface"
        claims, evidence = accepted(claim, [TX1, TX2]), self.evidence(TX3)
        path = next(iter(evidence))
        result_id = "result-bssc-shared-route-interface"
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX3,
            base_state_digest=state["stateDigest"], accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={
                "currentStateSummary": "A single interface result is shared by two local routes.",
                "localResidualSummary": "Root integration and route-local work remain.",
            },
            result_changes=[self.create_result(
                result_id=result_id, claim=claim, path=path,
                title="Shared route interface",
                statement="One interface result informs both the K1 and K2 work packages.",
                dependencies=[RESULT1, RESULT2A],
            )],
        )
        scope = self.scope(
            state, claims, write_programs=["root", PROGRAM1, PROGRAM2], write_results=[],
            create_programs=[], create_results=[result_id],
        )
        programs = []
        for program_id in (PROGRAM1, PROGRAM2):
            prior = state["programs"][program_id]
            programs.append({
                "action": "refresh", "programId": program_id,
                "baseDigest": prior["digest"], "parentId": prior["parentId"],
                "title": prior["title"], "objective": prior["objective"],
                "currentStateSummary": f"{program_id} now exposes one shared route interface.",
                "localResidualSummary": prior["localResidualSummary"], "status": prior["status"],
            })
        response = self.response(
            state=state, accounting=accounting, boundary_state=boundaries,
            packet=packet, scope=scope, programs=programs,
            placements=[{
                "resultId": result_id, "primaryProgramId": PROGRAM1,
                "relatedProgramIds": [PROGRAM2],
            }],
            affected=[PROGRAM1, PROGRAM2, "root"],
            assessments=[
                self.assessment(PROGRAM1, "180", "0.5", packet, claim),
                self.assessment(PROGRAM2, "0", "1", packet, claim),
                self.assessment("root", "950", None, packet, claim),
            ],
            rationale="The shared result stays singular rather than being duplicated by owner.",
        )
        reduced = self.reduce({
            "state": state, "accounting": accounting, "boundaries": boundaries,
            "packet": packet, "scope": scope, "claims": claims,
            "evidence": evidence, "judgment": "sha256:" + "3" * 64,
            "response": response,
        })
        result = reduced["postState"]["intermediateResults"][result_id]
        self.assertEqual(result["primaryProgramId"], PROGRAM1)
        self.assertEqual(result["relatedProgramIds"], [PROGRAM2])
        self.assertEqual(
            reduced["postState"]["contributions"][TX3]["directProgramIds"],
            [PROGRAM1, PROGRAM2],
        )
        self.assertEqual(
            reduced["accountingAffectedProgramIds"],
            [PROGRAM1, PROGRAM2, "root"],
        )

    def test_completed_status_is_expressible(self) -> None:
        k1, _ = self.k1(); k2, _ = self.k2(k1); k3, _ = self.k3(k2, completed=True)
        self.assertEqual(k3["postState"]["programs"][PROGRAM2]["status"], "completed")

    def test_changed_meaning_requires_new_result_and_explicit_supersession(self) -> None:
        k1, _ = self.k1(); k2, _ = self.k2(k1)
        state, accounting, boundaries = k2["postState"], k2["withAccessState"], k2["boundaryState"]
        claim = f"{PROBLEM}/k3-revised-uv-theorem"
        claims, evidence = accepted(claim, [TX2]), self.evidence(TX3)
        path = next(iter(evidence))
        successor = "result-uv-average-product-additivity-revised"
        prior = state["intermediateResults"][RESULT2A]
        old = self.result_change(
            action="supersede", result_id=RESULT2A, claim_keys=[], evidence_path=path,
            base=prior, status="superseded", successors=[successor],
        )
        new = self.create_result(
            result_id=successor, claim=claim, path=path,
            title="Revised UV product theorem",
            statement="A genuinely different qualified UV theorem replaces the old meaning.",
            dependencies=[RESULT2A],
        )
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX3,
            base_state_digest=state["stateDigest"], accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={"currentStateSummary": "A revised UV theorem explicitly supersedes one prior result.", "localResidualSummary": "Other work remains."},
            result_changes=sorted([old, new], key=lambda row: row["id"]),
        )
        scope = self.scope(
            state, claims, write_programs=["root", PROGRAM2],
            write_results=[RESULT2A], create_programs=[], create_results=[successor],
        )
        prior_program = state["programs"][PROGRAM2]
        program = {
            "action": "refresh", "programId": PROGRAM2, "baseDigest": prior_program["digest"],
            "parentId": prior_program["parentId"], "title": prior_program["title"],
            "objective": prior_program["objective"],
            "currentStateSummary": "The revised theorem supersedes the earlier average-additivity result.",
            "localResidualSummary": prior_program["localResidualSummary"], "status": "active",
        }
        response = self.response(
            state=state, accounting=accounting, boundary_state=boundaries,
            packet=packet, scope=scope, programs=[program],
            placements=[
                {"resultId": RESULT2A, "primaryProgramId": PROGRAM2, "relatedProgramIds": []},
                {"resultId": successor, "primaryProgramId": PROGRAM2, "relatedProgramIds": []},
            ], affected=["root", PROGRAM2],
            assessments=[self.assessment(PROGRAM2, "0", "1", packet, claim), self.assessment("root", "840", None, packet, claim)],
            rationale="Changed meaning uses a new result ID and explicit predecessor supersession.",
        )
        reduced = self.reduce({
            "state": state, "accounting": accounting, "boundaries": boundaries,
            "packet": packet, "scope": scope, "claims": claims, "evidence": evidence,
            "judgment": "sha256:" + "3" * 64, "response": response,
        })
        self.assertEqual(reduced["postState"]["intermediateResults"][RESULT2A]["status"], "superseded")
        self.assertEqual(reduced["postState"]["intermediateResults"][RESULT2A]["supersededByResultIds"], [successor])
        self.assertEqual(reduced["postState"]["intermediateResults"][successor]["status"], "active")
        self.assertEqual(
            reduced["postState"]["contributions"][TX3]["intermediateResultIds"],
            [successor],
        )
        old_claims = reduced["postState"]["intermediateResults"][RESULT2A]["claimRefs"]
        self.assertFalse(any(row["transactionId"] == TX3 for row in old_claims))

    def retirement_inputs(self) -> dict[str, object]:
        k1, _ = self.k1(); k2, _ = self.k2(k1)
        state, accounting, boundaries = k2["postState"], k2["withAccessState"], k2["boundaryState"]
        claim = f"{PROBLEM}/k3-prune-uv-package"
        claims, evidence = accepted(claim, [TX2]), self.evidence(TX3)
        path = next(iter(evidence))
        pruning_result = "result-uv-package-pruned"
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX3,
            base_state_digest=state["stateDigest"], accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={"currentStateSummary": "The obsolete UV package is retired.", "localResidualSummary": "The root continues through other routes."},
            result_changes=sorted([
                self.result_change(
                    action="retire", result_id=result_id, claim_keys=[],
                    evidence_path=path, base=state["intermediateResults"][result_id],
                    status="retired",
                )
                for result_id in (RESULT2A, RESULT2B)
            ] + [self.create_result(
                result_id=pruning_result, claim=claim, path=path,
                title="UV package pruning result",
                statement="The represented UV package can be pruned from the live portfolio.",
                dependencies=[RESULT2A, RESULT2B],
            )], key=lambda row: row["id"]),
        )
        scope = self.scope(
            state, claims, write_programs=["root", PROGRAM2],
            write_results=[RESULT2A, RESULT2B], create_programs=[],
            create_results=[pruning_result],
        )
        prior = state["programs"][PROGRAM2]
        program = {
            "action": "retire", "programId": PROGRAM2, "baseDigest": prior["digest"],
            "parentId": prior["parentId"], "title": prior["title"], "objective": prior["objective"],
            "currentStateSummary": prior["currentStateSummary"], "localResidualSummary": prior["localResidualSummary"],
            "status": "retired",
        }
        response = self.response(
            state=state, accounting=accounting, boundary_state=boundaries,
            packet=packet, scope=scope, programs=[program],
            placements=[
                {"resultId": result_id, "primaryProgramId": PROGRAM2, "relatedProgramIds": []}
                for result_id in (RESULT2A, RESULT2B)
            ] + [{"resultId": pruning_result, "primaryProgramId": "root", "relatedProgramIds": []}], affected=["root", PROGRAM2],
            assessments=[self.assessment(PROGRAM2, "0", "0", packet, claim), self.assessment("root", "900", None, packet, claim)],
            rationale="The program and both owned results are pruned and retired atomically.",
        )
        return {
            "state": state, "accounting": accounting, "boundaries": boundaries,
            "packet": packet, "scope": scope, "claims": claims, "evidence": evidence,
            "judgment": "sha256:" + "3" * 64, "response": response,
        }

    def test_program_and_results_can_be_retired_as_one_pruned_package(self) -> None:
        inputs = self.retirement_inputs()
        reduced = self.reduce(inputs)
        self.assertEqual(reduced["postState"]["programs"][PROGRAM2]["status"], "retired")
        self.assertTrue(all(reduced["postState"]["intermediateResults"][result_id]["status"] == "retired" for result_id in (RESULT2A, RESULT2B)))
        self.assertEqual(
            reduced["postState"]["contributions"][TX3]["intermediateResultIds"],
            ["result-uv-package-pruned"],
        )
        self.assertEqual(reduced["postState"]["contributions"][TX3]["directProgramIds"], ["root"])

    def test_multiple_program_retire_only_operations_are_pure_pruning(self) -> None:
        k1, _ = self.k1(); k2, _ = self.k2(k1)
        state, accounting, boundaries = (
            k2["postState"], k2["withAccessState"], k2["boundaryState"]
        )
        claim = f"{PROBLEM}/k3-prune-both-packages"
        claims, evidence = accepted(claim, [TX1, TX2]), self.evidence(TX3)
        path = next(iter(evidence))
        pruning_result = "result-both-packages-pruned"
        retired_results = (RESULT1, RESULT2A, RESULT2B)
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM, subject_transaction_id=TX3,
            base_state_digest=state["stateDigest"], accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update={
                "currentStateSummary": "Both obsolete packages are retired.",
                "localResidualSummary": "The root continues through other routes.",
            },
            result_changes=sorted(
                [
                    self.result_change(
                        action="retire", result_id=result_id, claim_keys=[],
                        evidence_path=path,
                        base=state["intermediateResults"][result_id], status="retired",
                    )
                    for result_id in retired_results
                ]
                + [
                    self.create_result(
                        result_id=pruning_result, claim=claim, path=path,
                        title="Joint package pruning result",
                        statement="Both represented packages can be pruned.",
                        dependencies=list(retired_results),
                    )
                ],
                key=lambda row: row["id"],
            ),
        )
        scope = self.scope(
            state, claims, write_programs=["root", PROGRAM1, PROGRAM2],
            write_results=list(retired_results), create_programs=[],
            create_results=[pruning_result],
        )
        program_changes = []
        for program_id in (PROGRAM1, PROGRAM2):
            prior = state["programs"][program_id]
            program_changes.append({
                "action": "retire", "programId": program_id,
                "baseDigest": prior["digest"], "parentId": prior["parentId"],
                "title": prior["title"], "objective": prior["objective"],
                "currentStateSummary": prior["currentStateSummary"],
                "localResidualSummary": prior["localResidualSummary"],
                "status": "retired",
            })
        placements = [
            {
                "resultId": result_id,
                "primaryProgramId": state["intermediateResults"][result_id][
                    "primaryProgramId"
                ],
                "relatedProgramIds": state["intermediateResults"][result_id][
                    "relatedProgramIds"
                ],
            }
            for result_id in retired_results
        ] + [{
            "resultId": pruning_result, "primaryProgramId": "root",
            "relatedProgramIds": [],
        }]
        response = self.response(
            state=state, accounting=accounting, boundary_state=boundaries,
            packet=packet, scope=scope, programs=program_changes,
            placements=placements, affected=["root", PROGRAM1, PROGRAM2],
            assessments=[
                self.assessment(PROGRAM1, "0", "0", packet, claim),
                self.assessment(PROGRAM2, "0", "0", packet, claim),
                self.assessment("root", "900", None, packet, claim),
            ],
            rationale="Both programs are pruned with no successor program.",
        )
        reduced = self.reduce({
            "state": state, "accounting": accounting, "boundaries": boundaries,
            "packet": packet, "scope": scope, "claims": claims,
            "evidence": evidence, "judgment": "sha256:" + "3" * 64,
            "response": response,
        })
        self.assertTrue(all(
            reduced["postState"]["programs"][program_id]["status"] == "retired"
            for program_id in (PROGRAM1, PROGRAM2)
        ))
        self.assertEqual(
            reduced["postState"]["contributions"][TX3]["directProgramIds"], ["root"]
        )

    def test_program_retire_cannot_accompany_create_refresh_or_move(self) -> None:
        mutations: list[tuple[str, dict[str, object], list[str], list[str]]] = []

        created = {
            "action": "create", "programId": "program-anonymous-successor",
            "baseDigest": None, "parentId": "root", "title": "Anonymous successor",
            "objective": "Continue the retired package without explicit lineage.",
            "currentStateSummary": "A replacement package appears.",
            "localResidualSummary": "Replacement work remains.", "status": "active",
        }
        mutations.append(("create", created, [], ["program-anonymous-successor"]))

        base_inputs = self.retirement_inputs()
        prior_program = base_inputs["state"]["programs"][PROGRAM1]
        refreshed = {
            "action": "refresh", "programId": PROGRAM1,
            "baseDigest": prior_program["digest"], "parentId": prior_program["parentId"],
            "title": prior_program["title"], "objective": prior_program["objective"],
            "currentStateSummary": "The surviving route absorbs replacement work.",
            "localResidualSummary": prior_program["localResidualSummary"],
            "status": prior_program["status"],
        }
        mutations.append(("refresh", refreshed, [PROGRAM1], []))

        moved = {
            "action": "move", "programId": PROGRAM1,
            "baseDigest": prior_program["digest"], "parentId": PROGRAM2,
            "title": prior_program["title"], "objective": prior_program["objective"],
            "currentStateSummary": prior_program["currentStateSummary"],
            "localResidualSummary": prior_program["localResidualSummary"],
            "status": prior_program["status"],
        }
        mutations.append(("move", moved, [PROGRAM1], []))

        for label, mutation, extra_writes, creates in mutations:
            with self.subTest(action=label):
                inputs = self.retirement_inputs()
                inputs["scope"] = self.scope(
                    inputs["state"], inputs["claims"],
                    write_programs=sorted({"root", PROGRAM2, *extra_writes}),
                    write_results=[RESULT2A, RESULT2B],
                    create_programs=creates,
                    create_results=["result-uv-package-pruned"],
                )
                inputs["response"]["authoringPacketDigest"] = inputs["scope"][
                    "authoringPacketDigest"
                ]
                inputs["response"]["programChanges"] = sorted(
                    [*inputs["response"]["programChanges"], mutation],
                    key=lambda row: row["programId"],
                )
                with self.assertRaisesRegex(
                    MathFlowError,
                    "program retirement cannot accompany create, refresh, or move",
                ):
                    self.reduce(inputs)

    def test_anonymous_one_to_two_program_successor_split_is_rejected(self) -> None:
        inputs = self.retirement_inputs()
        successor_ids = ["program-anonymous-successor-a", "program-anonymous-successor-b"]
        inputs["scope"] = self.scope(
            inputs["state"], inputs["claims"],
            write_programs=["root", PROGRAM2],
            write_results=[RESULT2A, RESULT2B],
            create_programs=successor_ids,
            create_results=["result-uv-package-pruned"],
        )
        inputs["response"]["authoringPacketDigest"] = inputs["scope"][
            "authoringPacketDigest"
        ]
        successors = [
            {
                "action": "create", "programId": program_id, "baseDigest": None,
                "parentId": "root", "title": f"Anonymous successor {index}",
                "objective": "Continue one anonymous portion of the retired package.",
                "currentStateSummary": "A successor package appears without lineage.",
                "localResidualSummary": "Successor work remains.", "status": "active",
            }
            for index, program_id in enumerate(successor_ids, start=1)
        ]
        inputs["response"]["programChanges"] = sorted(
            [*inputs["response"]["programChanges"], *successors],
            key=lambda row: row["programId"],
        )
        affected = ["root", PROGRAM2, *successor_ids]
        inputs["response"]["programBoundaries"] = [
            boundary(program_id) for program_id in sorted(affected)
        ]
        claim = str(inputs["claims"][0]["claimKey"])
        inputs["response"]["withAccessAssessments"] = sorted(
            [
                self.assessment(PROGRAM2, "0", "0", inputs["packet"], claim),
                self.assessment(successor_ids[0], "40", "0.5", inputs["packet"], claim),
                self.assessment(successor_ids[1], "60", "0.5", inputs["packet"], claim),
                self.assessment("root", "900", None, inputs["packet"], claim),
            ],
            key=lambda row: row["programId"],
        )
        inputs["response"]["topologyRationale"] = (
            "The retired program is anonymously replaced by two successor packages."
        )
        with self.assertRaisesRegex(
            MathFlowError,
            "program retirement cannot accompany create, refresh, or move",
        ):
            self.reduce(inputs)

    def test_move_refresh_is_rejected_but_pure_move_is_explicit(self) -> None:
        k1, _ = self.k1(); k2, _ = self.k2(k1); _, inputs = self.k3(k2)
        inputs = copy.deepcopy(inputs)
        inputs["scope"] = self.scope(
            inputs["state"], inputs["claims"],
            write_programs=["root", PROGRAM1, PROGRAM2],
            write_results=[RESULT2A, RESULT2B], create_programs=[], create_results=[],
        )
        inputs["response"]["authoringPacketDigest"] = inputs["scope"]["authoringPacketDigest"]
        prior = k2["postState"]["programs"][PROGRAM2]
        inputs["response"]["programChanges"][0].update({"action": "move", "parentId": PROGRAM1, "currentStateSummary": prior["currentStateSummary"]})
        inputs["response"]["programBoundaries"] = [boundary(program) for program in sorted([PROGRAM1, PROGRAM2, "root"])]
        inputs["response"]["withAccessAssessments"] = sorted([
            *inputs["response"]["withAccessAssessments"],
            self.assessment(PROGRAM1, "200", "0.5", inputs["packet"], f"{PROBLEM}/k3-uv-verification"),
        ], key=lambda row: row["programId"])
        inputs["response"]["topologyRationale"] = "Move the independent route under a new accounting parent."
        moved = self.reduce(inputs)
        self.assertEqual(moved["postState"]["programs"][PROGRAM2]["parentId"], PROGRAM1)
        invalid = copy.deepcopy(inputs)
        invalid["response"]["programChanges"][0]["currentStateSummary"] = "Move and refresh simultaneously."
        with self.assertRaisesRegex(MathFlowError, r"move\+refresh"):
            self.reduce(invalid)

    def test_typed_wplus_evidence_must_resolve(self) -> None:
        _, inputs = self.k1()
        inputs = copy.deepcopy(inputs)
        inputs["response"]["withAccessAssessments"][0]["evidenceRefs"][0]["digest"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(MathFlowError, "does not resolve"):
            self.reduce(inputs)

    def test_prior_typed_evidence_must_be_in_exact_v10_read_set(self) -> None:
        k1, _ = self.k1()
        _, inputs = self.k2(k1)
        cases = (
            (
                "prior-program",
                PROGRAM1,
                k1["postState"]["programs"][PROGRAM1]["digest"],
            ),
            (
                "prior-result",
                RESULT1,
                k1["postState"]["intermediateResults"][RESULT1]["digest"],
            ),
        )
        for kind, identifier, digest in cases:
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(MathFlowError, "does not resolve"):
                    _validate_evidence_refs(
                        [{"kind": kind, "id": identifier, "digest": digest}],
                        semantic_packet=inputs["packet"],
                        base_state=inputs["state"],
                        evidence_file_refs=inputs["evidence"],
                        readable_program_ids=set(),
                        readable_result_ids=set(),
                    )

    def test_stale_response_bindings_fail_before_reduction(self) -> None:
        _, inputs = self.k1()
        for field in (
            "baseStateDigest",
            "baseAccountingStateDigest",
            "baseBoundaryStateDigest",
            "semanticPacketDigest",
            "authoringPacketDigest",
        ):
            with self.subTest(field=field):
                stale = copy.deepcopy(inputs)
                stale["response"][field] = "sha256:" + "f" * 64
                with self.assertRaisesRegex(MathFlowError, f"stale {field}"):
                    self.reduce(stale)

    def test_rehashed_evidence_substitution_fails_semantic_binding(self) -> None:
        _, inputs = self.k1()
        substituted = {
            path: "sha256:" + "e" * 64
            for path in inputs["evidence"]
        }
        with self.assertRaisesRegex(MathFlowError, "evidence binding is stale"):
            self.reduce({**inputs, "evidence": substituted})

    def test_program_write_outside_local_scope_fails(self) -> None:
        k1, _ = self.k1()
        _, inputs = self.k2(k1)
        inputs = copy.deepcopy(inputs)
        prior = k1["postState"]["programs"][PROGRAM1]
        inputs["response"]["programChanges"] = sorted([
            *inputs["response"]["programChanges"],
            {
                "action": "refresh", "programId": PROGRAM1,
                "baseDigest": prior["digest"], "parentId": prior["parentId"],
                "title": prior["title"], "objective": prior["objective"],
                "currentStateSummary": "Illicit out-of-scope refresh.",
                "localResidualSummary": prior["localResidualSummary"],
                "status": prior["status"],
            },
        ], key=lambda row: row["programId"])
        inputs["response"]["programBoundaries"] = sorted([
            *inputs["response"]["programBoundaries"], boundary(PROGRAM1),
        ], key=lambda row: row["programId"])
        claim = f"{PROBLEM}/k2-uv-chain"
        inputs["response"]["withAccessAssessments"] = sorted([
            *inputs["response"]["withAccessAssessments"],
            self.assessment(PROGRAM1, "200", "0.5", inputs["packet"], claim),
        ], key=lambda row: row["programId"])
        with self.assertRaisesRegex(MathFlowError, "stale scope guard"):
            self.reduce(inputs)

    def test_lifecycle_change_cannot_attach_new_claim_to_old_semantics(self) -> None:
        k1, _ = self.k1()
        k2, _ = self.k2(k1)
        _, inputs = self.k3(k2)
        packet = copy.deepcopy(inputs["packet"])
        packet["resultChanges"][0]["action"] = "retire"
        packet["resultChanges"][0]["status"] = "retired"
        core = {key: value for key, value in packet.items() if key != "packetDigest"}
        packet["packetDigest"] = f"sha256:{sha256_json(core)}"
        with self.assertRaisesRegex(MathFlowError, "cannot treat the new claim as support"):
            self.reduce({**inputs, "packet": packet})

    def test_tampered_cumulative_boundary_state_fails_before_reduction(self) -> None:
        _, inputs = self.k1()
        tampered = copy.deepcopy(inputs["boundaries"])
        tampered["boundaries"][0]["activationCondition"] += " Tampered."
        with self.assertRaisesRegex(MathFlowError, "boundary digest mismatch"):
            self.reduce({**inputs, "boundaries": tampered})

    def test_v2_schema_binds_boundary_state(self) -> None:
        _, inputs = self.k1()
        schema = joint_portfolio_serial_response_schema_v2(
            subject_transaction_id=TX1, base_state_digest=self.origin["stateDigest"],
            base_accounting_state_digest=self.accounting_origin["stateDigest"],
            base_boundary_state_digest=self.boundary_origin["stateDigest"],
            semantic_packet_digest=inputs["packet"]["packetDigest"], authoring_packet_digest=inputs["scope"]["authoringPacketDigest"],
        )
        self.assertEqual(schema["properties"]["baseBoundaryStateDigest"]["const"], self.boundary_origin["stateDigest"])

    def test_replays_actual_successful_k1_state_and_k2_two_result_response(self) -> None:
        experiment = ROOT / "protocol/experiments/bssc-joint-portfolio-wplus-k2-v3"
        state = validate_research_program_state_v3(json.loads((experiment / "fixtures/k1-post-state.json").read_text()))
        accounting = validate_work_accounting_state(
            json.loads((experiment / "fixtures/k1-with-access-state.json").read_text()),
            state,
            self.contract,
        )
        self.assertEqual(
            state["stateDigest"],
            "sha256:03710af10c1c9efb7796d5ae0457b016af0d1bb185818fa60425ac80021bfda4",
        )
        self.assertEqual(accounting["totalWorkHours"], "4451.7375")
        self.assertEqual(
            accounting["stateDigest"],
            "sha256:dfdd463b09b28555dbfb61a53df48c1006dcfe9bf811da3b2e34b64acfadfe0d",
        )
        fixed = json.loads((experiment / "fixed-semantic-packet-v3.json").read_text())
        observed = json.loads((experiment / "fixtures/successful-response-run-33564954137.json").read_text())
        subject = fixed["subjectTransactionId"]
        claim = fixed["intermediateResults"][0]["claimKeys"][0]
        claims = accepted(claim, ["c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6"])
        paths = sorted({path for result in fixed["intermediateResults"] for path in result["support"]["artifactPaths"]})
        evidence = {path: sha256_bytes((ROOT / path).read_bytes()) for path in paths}
        packet = make_joint_portfolio_semantic_packet_v2(
            problem_id=PROBLEM,
            subject_transaction_id=subject,
            base_state_digest=state["stateDigest"],
            accepted_claims=claims,
            evidence_file_refs=evidence,
            root_update=fixed["rootUpdate"],
            result_changes=[
                {
                    "action": "create", "id": result["id"], "baseDigest": None,
                    "title": result["title"], "statement": result["statement"],
                    "scopeQualifications": result["scopeQualifications"],
                    "supportAdditions": result["support"],
                    "dependencyResultIds": result["dependencyResultIds"],
                    "claimKeys": result["claimKeys"], "status": "active",
                    "supersededByResultIds": [],
                }
                for result in fixed["intermediateResults"]
            ],
        )
        context = build_research_builder_v10_route_context(state, claims)
        external_dependencies = sorted({dependency for result in fixed["intermediateResults"] for dependency in result["dependencyResultIds"] if dependency in state["intermediateResults"]})
        route = {
            "schemaVersion": 1, "baseStateDigest": state["stateDigest"],
            "routeContextDigest": context["contextDigest"], "inspectProgramIds": [],
            "inspectResultIds": external_dependencies, "searchQueries": [],
            "writeProgramIds": ["root"], "writeResultIds": [],
            "createProgramIds": [observed["createdPrograms"][0]["id"]],
            "createResultIds": sorted(result["id"] for result in fixed["intermediateResults"]),
        }
        scope = build_research_builder_v10_authoring_packet(
            state, claims, route, route_context=context, max_programs=24, max_results=24,
        )
        predecessor_boundaries = make_joint_portfolio_boundary_state_v1(
            knowledge_state=state,
            boundaries=[boundary(program_id) for program_id in sorted(state["programs"])],
        )
        program = observed["createdPrograms"][0]
        program_change = {
            "action": "create", "programId": program["id"], "baseDigest": None,
            "parentId": program["parentId"], "title": program["title"],
            "objective": program["objective"], "currentStateSummary": program["currentStateSummary"],
            "localResidualSummary": program["localResidualSummary"], "status": "active",
        }
        response = {
            "schemaVersion": 2, "subjectTransactionId": subject,
            "baseStateDigest": state["stateDigest"], "baseAccountingStateDigest": accounting["stateDigest"],
            "baseBoundaryStateDigest": predecessor_boundaries["stateDigest"],
            "semanticPacketDigest": packet["packetDigest"], "authoringPacketDigest": scope["authoringPacketDigest"],
            "programChanges": [program_change],
            "resultPlacements": [
                {"resultId": row["resultId"], "primaryProgramId": row["primaryProgramId"], "relatedProgramIds": []}
                for row in observed["resultPlacements"]
            ],
            "programBoundaries": sorted([
                observed["createdProgramBoundaries"][0],
                {"programId": "root", **observed["rootBoundary"]},
            ], key=lambda row: row["programId"]),
            "withAccessAssessments": sorted([
                {
                    **observed["createdProgramWithAccessAnnotations"][0],
                    "evidenceRefs": self.claims_ref(packet, claim),
                },
                {
                    "programId": "root", "directWorkHours": observed["rootWithAccessAnnotation"]["directWorkHours"],
                    "conditionalIncidence": None, "rationale": observed["rootWithAccessAnnotation"]["rationale"],
                    "evidenceRefs": self.claims_ref(packet, claim),
                },
            ], key=lambda row: row["programId"]),
            "topologyRationale": observed["topologyRationale"],
        }
        reduced = reduce_joint_portfolio_serial_transition_v2(
            response, base_state=state, base_accounting_state=accounting,
            base_boundary_state=predecessor_boundaries, root_contract=self.contract,
            semantic_packet=packet, authoring_packet=scope, accepted_claims=claims,
            judgment_id="sha256:" + "2" * 64, evidence_file_refs=evidence,
        )
        self.assertEqual(reduced["withAccessState"]["totalWorkHours"], "4351.7375")
        self.assertEqual(
            f"sha256:{sha256_json(reduced)}",
            "sha256:28e15a36e848c69192d6e29d490aa2029ee003f0da2d7e3df5d7977c6a72e602",
        )
        self.assertEqual(
            set(reduced["postState"]["programs"][program["id"]]["intermediateResultIds"]),
            {RESULT2A, RESULT2B},
        )


if __name__ == "__main__":
    unittest.main()
