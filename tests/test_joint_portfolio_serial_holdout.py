from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from math_flow.artifacts import sha256_bytes
from math_flow.errors import MathFlowError
from math_flow.joint_portfolio_serial_holdout import (
    K1_PROGRAM,
    K2_PROGRAM,
    K2_RESULTS,
    SUBJECTS,
    load_bssc_joint_portfolio_serial_holdout_bundle_v1,
    run_bssc_joint_portfolio_serial_holdout_v1,
)
from math_flow.joint_portfolio_serial_credit_v2 import (
    OpenRouterJointPortfolioSerialCreditV2Provider,
)
from math_flow.joint_portfolio_serial_provider_v2 import (
    OpenRouterJointPortfolioSerialAuthorV2Provider,
)
from math_flow.repository import sha256_json


ROOT = Path(__file__).resolve().parents[1]


def _object_digest(value: object) -> str:
    return f"sha256:{sha256_json(value)}"


def _boundary(program_id: str) -> dict[str, str]:
    return {
        "programId": program_id,
        "directResidualWorkScope": f"Direct residual work assigned only to {program_id}.",
        "activationCondition": f"Activate {program_id} while its local route is live.",
        "stoppingCondition": f"Stop {program_id} when its local route is solved or pruned.",
        "independentVariationRationale": (
            f"The inclusion and stopping decision for {program_id} can vary independently."
        ),
    }


def _claim_ref(request: dict[str, object]) -> dict[str, str]:
    semantic = request["semanticPacket"]
    claims = request["acceptedClaimAssessments"]
    return {
        "kind": "accepted-claim",
        "id": str(claims[0]["claimKey"]),
        "digest": str(semantic["acceptedClaimsDigest"]),
    }


def _assessment(
    request: dict[str, object], program_id: str, direct: str, incidence: str | None
) -> dict[str, object]:
    return {
        "programId": program_id,
        "directWorkHours": direct,
        "conditionalIncidence": incidence,
        "rationale": f"The accepted subject updates the live work policy at {program_id}.",
        "evidenceRefs": [_claim_ref(request)],
    }


class FixtureJointAuthorProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    def __call__(self, *, stage, request, evidence_files):
        evidence = tuple(evidence_files)
        subject = str(request["subjectTransactionId"])
        self.calls.append((stage, subject, len(evidence)))
        if stage != "joint-author" or not evidence:
            raise AssertionError("the fixture author requires the isolated joint-author stage")
        if "baseState" in request:
            state = request["baseState"]
            state_digest = state["stateDigest"]
            accounting_digest = request["baseAccountingState"]["stateDigest"]
            boundary_digest = request["baseBoundaryState"]["stateDigest"]
        else:
            state = {
                "programs": request["baseKnowledgeContext"]["programs"],
                "intermediateResults": request["baseKnowledgeContext"][
                    "intermediateResults"
                ],
            }
            state_digest = request["bindings"]["baseKnowledgeStateDigest"]
            accounting_digest = request["bindings"]["baseAccountingStateDigest"]
            boundary_digest = request["bindings"]["baseBoundaryStateDigest"]
        semantic = request["semanticPacket"]
        authoring = request["authoringPacket"]
        ordinal = SUBJECTS.index(subject) + 1
        if ordinal == 1:
            program_id = K1_PROGRAM
            program_changes = [
                {
                    "action": "create",
                    "programId": program_id,
                    "baseDigest": None,
                    "parentId": "root",
                    "title": "Code-induced converse structure",
                    "objective": "Develop the code-induced BSSC converse route.",
                    "currentStateSummary": "Two accepted K1 results establish the represented structure.",
                    "localResidualSummary": "Structure-preserving refinements remain.",
                    "status": "active",
                }
            ]
            assessments = [
                _assessment(request, program_id, "200", "0.5"),
                _assessment(request, "root", "1000", None),
            ]
            rationale = "One durable K1 accounting package owns both accepted results."
        elif ordinal == 2:
            program_id = K2_PROGRAM
            program_changes = [
                {
                    "action": "create",
                    "programId": program_id,
                    "baseDigest": None,
                    "parentId": "root",
                    "title": "Relaxed UV product and symmetry route",
                    "objective": "Resolve the separately relaxed UV scalar theorem chain.",
                    "currentStateSummary": "The two-result theorem chain is established.",
                    "localResidualSummary": "No direct work remains in this narrow theorem package.",
                    "status": "active",
                }
            ]
            assessments = [
                _assessment(request, program_id, "0", "1"),
                _assessment(request, "root", "900", None),
            ]
            rationale = "The two dependent results share one stopping policy."
        else:
            program_id = K2_PROGRAM
            prior = state["programs"][program_id]
            program_changes = [
                {
                    "action": "refresh",
                    "programId": program_id,
                    "baseDigest": prior["digest"],
                    "parentId": prior["parentId"],
                    "title": prior["title"],
                    "objective": prior["objective"],
                    "currentStateSummary": (
                        "The exact K2 theorem chain now has independent accepted support."
                    ),
                    "localResidualSummary": prior["localResidualSummary"],
                    "status": prior["status"],
                }
            ]
            assessments = [
                _assessment(request, program_id, "10", "0.5"),
                _assessment(request, "root", "850", None),
            ]
            rationale = None
        placements = [
            {
                "resultId": change["id"],
                "primaryProgramId": program_id,
                "relatedProgramIds": [],
            }
            for change in semantic["resultChanges"]
        ]
        affected = sorted([program_id, "root"])
        return {
            "schemaVersion": 2,
            "subjectTransactionId": subject,
            "baseStateDigest": state_digest,
            "baseAccountingStateDigest": accounting_digest,
            "baseBoundaryStateDigest": boundary_digest,
            "semanticPacketDigest": semantic["packetDigest"],
            "authoringPacketDigest": authoring["authoringPacketDigest"],
            "programChanges": program_changes,
            "resultPlacements": sorted(placements, key=lambda row: row["resultId"]),
            "programBoundaries": [_boundary(program) for program in affected],
            "withAccessAssessments": sorted(
                assessments, key=lambda row: row["programId"]
            ),
            "topologyRationale": rationale,
        }


class FixtureCreditProvider:
    def __init__(self, *, reject_k2_once: bool = False) -> None:
        self.reject_k2_once = reject_k2_once
        self.calls: list[tuple[str, str, int]] = []

    def __call__(self, *, stage, request, evidence_files):
        evidence = tuple(evidence_files)
        subject = str(request["subjectTransactionId"])
        self.calls.append((stage, subject, len(evidence)))
        ordinal = SUBJECTS.index(subject) + 1
        affected = [K1_PROGRAM, "root"] if ordinal == 1 else [K2_PROGRAM, "root"]
        if stage == "safe-facts":
            if not evidence:
                raise AssertionError("safe facts require canonical submission bytes")
            claim_key = request["stageInput"]["acceptedClaimRefs"][0]["claimKey"]
            return {
                "facts": [
                    {
                        "id": "realized-result-condition",
                        "condition": "The accepted result holds in the realized same world.",
                        "actorVisibility": "withheld-until-independent-discovery",
                        "affectedNodeRefs": [
                            {"kind": "program", "id": program}
                            for program in sorted(affected)
                        ],
                        "acceptedClaimKeys": [claim_key],
                    }
                ],
                "assumptions": [
                    "The no-access community follows the pre-submission work policy."
                ],
            }
        if stage != "no-access" or evidence:
            raise AssertionError("the no-access stage must receive no raw evidence")
        if ordinal == 1:
            updates = [
                {
                    "nodeRef": {"kind": "program", "id": K1_PROGRAM},
                    "changes": {
                        "directWorkHours": "200",
                        "conditionalIncidence": "0.5",
                    },
                    "rationale": "The no-access community still has to establish K1.",
                    "evidenceRefs": ["safe-fact:realized-result-condition"],
                },
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "changes": {"directWorkHours": "1200"},
                    "rationale": "Root discovery and integration work remains without K1.",
                    "evidenceRefs": ["safe-fact:realized-result-condition"],
                },
            ]
        elif ordinal == 2 and self.reject_k2_once:
            self.reject_k2_once = False
            updates = [
                {
                    "nodeRef": {"kind": "program", "id": K2_PROGRAM},
                    "changes": {
                        "directWorkHours": "0",
                        "conditionalIncidence": "1",
                    },
                    "rationale": "Deliberately invalid nonpositive fixture.",
                    "evidenceRefs": ["safe-fact:realized-result-condition"],
                },
                {
                    "nodeRef": {"kind": "program", "id": "root"},
                    "changes": {"directWorkHours": "800"},
                    "rationale": "Deliberately invalid nonpositive fixture.",
                    "evidenceRefs": ["safe-fact:realized-result-condition"],
                },
            ]
        elif ordinal == 2:
            updates = [
                {
                    "nodeRef": {"kind": "program", "id": K2_PROGRAM},
                    "changes": {
                        "directWorkHours": "200",
                        "conditionalIncidence": "1",
                    },
                    "rationale": "The UV theorem package remains without K2.",
                    "evidenceRefs": ["safe-fact:realized-result-condition"],
                }
            ]
        else:
            updates = []
        return {"updates": updates}


class OpenRouterFixtureTransport:
    def __init__(self) -> None:
        self.author = FixtureJointAuthorProvider()
        self.credit = FixtureCreditProvider()
        self.requests: list[dict[str, object]] = []
        self.stages: list[tuple[str, str]] = []

    @staticmethod
    def quoted_input(request: dict[str, object]) -> dict[str, object]:
        prefix = "<math-flow-input>\n"
        suffix = "\n</math-flow-input>"
        for message in reversed(request["messages"]):
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, str) or prefix not in content:
                continue
            raw = content.split(prefix, 1)[1]
            if not raw.endswith(suffix):
                raise AssertionError("malformed governed request")
            value = json.loads(raw[: -len(suffix)])
            if not isinstance(value, dict):
                raise AssertionError("governed request is not an object")
            return value
        raise AssertionError("governed request is missing")

    def __call__(self, request: dict[str, object]) -> dict[str, object]:
        self.requests.append(copy.deepcopy(request))
        user_data = self.quoted_input(request)
        if user_data.get("stage") == "joint-author":
            stage = "joint-author"
            subject = str(user_data["subjectTransactionId"])
            response = self.author(
                stage=stage,
                request=user_data,
                evidence_files=(object(),),
            )
        else:
            work_request = user_data["request"]
            stage = str(work_request["stage"])
            subject = str(work_request["subjectTransactionId"])
            response = self.credit(
                stage=stage,
                request=work_request,
                evidence_files=(object(),) if stage == "safe-facts" else (),
            )
        self.stages.append((stage, subject))
        return {
            "id": f"fixture-{len(self.requests)}",
            "model": "openai/gpt-5.6-sol",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(response)},
                }
            ],
        }


class JointPortfolioSerialHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name)
        cls.output = cls.base / "bundle"
        cls.checkpoints = cls.base / "checkpoints"
        cls.author_provider = FixtureJointAuthorProvider()
        cls.credit_provider = FixtureCreditProvider()
        cls.loaded = run_bssc_joint_portfolio_serial_holdout_v1(
            root=ROOT,
            output_dir=cls.output,
            checkpoint_dir=cls.checkpoints,
            joint_author_provider=cls.author_provider,
            credit_provider=cls.credit_provider,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def copied_bundle(self, name: str) -> Path:
        destination = self.base / name
        shutil.copytree(self.output, destination)
        return destination

    def rewrite_json_artifact(self, bundle: Path, role: str, value: object) -> None:
        run_path = bundle / "run.json"
        manifest = json.loads(run_path.read_text())
        entry = next(item for item in manifest["artifacts"] if item["role"] == role)
        raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
        (bundle / entry["path"]).write_bytes(raw)
        entry["digest"] = sha256_bytes(raw)
        entry["bytes"] = len(raw)
        run_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    def rewrite_manifest(self, bundle: Path, mutate) -> None:
        path = bundle / "run.json"
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")

    def rewrite_author_response_and_replay(
        self, bundle: Path, ordinal: int, response: object
    ) -> None:
        replay_path = bundle / f"steps/k{ordinal}/author/replay.json"
        replay = json.loads(replay_path.read_text())
        replay["response"] = response
        replay["responseDigest"] = _object_digest(response)
        replay["resultDigest"] = _object_digest(
            {key: value for key, value in replay.items() if key != "resultDigest"}
        )
        self.rewrite_json_artifact(
            bundle, f"joint-holdout-k{ordinal}-author-response", response
        )
        self.rewrite_json_artifact(
            bundle, f"joint-holdout-k{ordinal}-author-replay", replay
        )

    def test_complete_three_step_bundle_replays_and_gates_k3_reuse(self) -> None:
        experiment = json.loads(
            (
                ROOT
                / "protocol/experiments/bssc-joint-portfolio-serial-k1-k3-v1/manifest.json"
            ).read_text()
        )
        for field, bundled_path in (
            ("validitySource", "input/validity-source.json"),
            ("rootContract", "input/root-contract.json"),
            ("workJudgeSpec", "input/work-judge-spec.json"),
            ("jointAuthorJudgeSpec", "input/joint-author-judge-spec.json"),
        ):
            with self.subTest(bound_input=field):
                self.assertEqual(
                    (self.output / bundled_path).read_bytes(),
                    (ROOT / experiment[field]).read_bytes(),
                )
        self.assertEqual(
            [(stage, subject) for stage, subject, _ in self.author_provider.calls],
            [("joint-author", subject) for subject in SUBJECTS],
        )
        self.assertEqual(
            [(stage, subject) for stage, subject, _ in self.credit_provider.calls],
            [
                (stage, subject)
                for subject in SUBJECTS
                for stage in ("safe-facts", "no-access")
            ],
        )
        replay = load_bssc_joint_portfolio_serial_holdout_bundle_v1(
            self.output, expected_bundle_digest=self.loaded["bundleDigest"]
        )
        self.assertEqual(len(replay["steps"]), 3)
        for step in replay["steps"]:
            author = step["authorResult"]
            self.assertEqual(
                author["profile"], "math-flow/joint-portfolio-serial-author-v2"
            )
            self.assertEqual(author["requestDigest"], author["request"]["requestDigest"])
            self.assertEqual(
                author["requestEnvelopeDigest"], _object_digest(author["request"])
            )
        k3 = replay["steps"][2]["joint"]
        self.assertEqual(k3["transition"]["topologyOperations"], [])
        self.assertEqual(k3["accountingAffectedProgramIds"], [K2_PROGRAM, "root"])
        for result_id in K2_RESULTS:
            self.assertEqual(
                k3["postState"]["intermediateResults"][result_id][
                    "sourceTransactionIds"
                ],
                sorted([SUBJECTS[1], SUBJECTS[2]]),
            )

    def test_continue_and_publication_are_rejected_before_provider_calls(self) -> None:
        for field in ("continue_run", "publish"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                author_provider = FixtureJointAuthorProvider()
                with self.assertRaisesRegex(MathFlowError, "continue=false.*publication"):
                    run_bssc_joint_portfolio_serial_holdout_v1(
                        root=ROOT,
                        output_dir=Path(directory) / "output",
                        checkpoint_dir=Path(directory) / "checkpoints",
                        joint_author_provider=author_provider,
                        credit_provider=FixtureCreditProvider(),
                        **{field: True},
                    )
                self.assertEqual(author_provider.calls, [])

    def test_real_openrouter_adapters_compose_for_all_nine_stages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            transport = OpenRouterFixtureTransport()
            author_spec = json.loads(
                (
                    ROOT
                    / "protocol/judges/openrouter-joint-portfolio-serial-author-v2.json"
                ).read_text(encoding="utf-8")
            )
            work_spec = json.loads(
                (
                    ROOT / "protocol/judges/openrouter-work-accounting-v2.json"
                ).read_text(encoding="utf-8")
            )
            author = OpenRouterJointPortfolioSerialAuthorV2Provider(
                author_spec, transport=transport
            )
            credit = OpenRouterJointPortfolioSerialCreditV2Provider(
                work_spec, transport=transport
            )
            result = run_bssc_joint_portfolio_serial_holdout_v1(
                root=ROOT,
                output_dir=base / "bundle",
                checkpoint_dir=base / "checkpoints",
                joint_author_provider=author,
                credit_provider=credit,
            )

            self.assertEqual(len(result["steps"]), 3)
            self.assertEqual(
                transport.stages,
                [
                    (stage, subject)
                    for subject in SUBJECTS
                    for stage in ("joint-author", "safe-facts", "no-access")
                ],
            )
            self.assertEqual(len(author.invocation_records), 3)
            self.assertEqual(len(credit.invocation_records), 6)
            self.assertTrue(
                all(
                    len(json.dumps(request, sort_keys=True).encode("utf-8"))
                    < 4_000_000
                    for request in transport.requests
                )
            )

    def test_rejected_k2_wminus_retains_validated_author_and_safe_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            author_provider = FixtureJointAuthorProvider()
            credit = FixtureCreditProvider(reject_k2_once=True)
            with self.assertRaisesRegex(MathFlowError, "strictly positive"):
                run_bssc_joint_portfolio_serial_holdout_v1(
                    root=ROOT,
                    output_dir=base / "failed-output",
                    checkpoint_dir=base / "checkpoints",
                    joint_author_provider=author_provider,
                    credit_provider=credit,
                )
            self.assertEqual(
                [(stage, subject) for stage, subject, _ in author_provider.calls],
                [("joint-author", subject) for subject in SUBJECTS[:2]],
            )
            author_provider.calls.clear()
            credit.calls.clear()
            result = run_bssc_joint_portfolio_serial_holdout_v1(
                root=ROOT,
                output_dir=base / "accepted-output",
                checkpoint_dir=base / "checkpoints",
                joint_author_provider=author_provider,
                credit_provider=credit,
            )
            self.assertEqual(
                [(stage, subject) for stage, subject, _ in author_provider.calls],
                [("joint-author", SUBJECTS[2])],
            )
            self.assertEqual(
                [(stage, subject) for stage, subject, _ in credit.calls],
                [
                    ("no-access", SUBJECTS[1]),
                    ("safe-facts", SUBJECTS[2]),
                    ("no-access", SUBJECTS[2]),
                ],
            )
            self.assertEqual(len(result["steps"]), 3)

    def test_truncated_artifact_is_rejected(self) -> None:
        bundle = self.copied_bundle("truncated")
        (bundle / "steps/k2/author/response.json").unlink()
        with self.assertRaisesRegex(MathFlowError, "artifact is missing"):
            load_bssc_joint_portfolio_serial_holdout_bundle_v1(bundle)

    def test_substituted_response_is_reduced_against_its_exact_step(self) -> None:
        bundle = self.copied_bundle("substituted")
        response = json.loads((bundle / "steps/k2/author/response.json").read_text())
        self.rewrite_author_response_and_replay(bundle, 3, response)
        with self.assertRaisesRegex(MathFlowError, "subject|stale"):
            load_bssc_joint_portfolio_serial_holdout_bundle_v1(bundle)

    def test_reordered_step_bindings_are_rejected(self) -> None:
        bundle = self.copied_bundle("reordered")
        self.rewrite_manifest(
            bundle,
            lambda value: value["stepBindings"].__setitem__(
                slice(0, 2), list(reversed(value["stepBindings"][:2]))
            ),
        )
        with self.assertRaisesRegex(MathFlowError, "reordered"):
            load_bssc_joint_portfolio_serial_holdout_bundle_v1(bundle)

    def test_stale_response_binding_is_rejected_by_rereduction(self) -> None:
        bundle = self.copied_bundle("stale")
        response = json.loads((bundle / "steps/k2/author/response.json").read_text())
        response["baseAccountingStateDigest"] = "sha256:" + "0" * 64
        self.rewrite_author_response_and_replay(bundle, 2, response)
        with self.assertRaisesRegex(MathFlowError, "stale baseAccountingStateDigest"):
            load_bssc_joint_portfolio_serial_holdout_bundle_v1(bundle)

    def test_resealed_author_request_substitution_is_not_reproducible(self) -> None:
        bundle = self.copied_bundle("request-substitution")
        request = json.loads((bundle / "steps/k2/author/request.json").read_text())
        request["bindings"]["baseAccountingStateDigest"] = "sha256:" + "0" * 64
        request["requestDigest"] = _object_digest(
            {key: value for key, value in request.items() if key != "requestDigest"}
        )
        replay = json.loads((bundle / "steps/k2/author/replay.json").read_text())
        replay["request"] = request
        replay["requestDigest"] = request["requestDigest"]
        replay["requestEnvelopeDigest"] = _object_digest(request)
        replay["resultDigest"] = _object_digest(
            {key: value for key, value in replay.items() if key != "resultDigest"}
        )
        self.rewrite_json_artifact(
            bundle, "joint-holdout-k2-author-request", request
        )
        self.rewrite_json_artifact(
            bundle, "joint-holdout-k2-author-replay", replay
        )
        with self.assertRaisesRegex(MathFlowError, "request is not reproducible"):
            load_bssc_joint_portfolio_serial_holdout_bundle_v1(bundle)

    def test_skipped_frontier_binding_is_rejected(self) -> None:
        bundle = self.copied_bundle("skipped")
        self.rewrite_manifest(bundle, lambda value: value["stepBindings"].pop(1))
        with self.assertRaisesRegex(MathFlowError, "skipped"):
            load_bssc_joint_portfolio_serial_holdout_bundle_v1(bundle)


if __name__ == "__main__":
    unittest.main()
