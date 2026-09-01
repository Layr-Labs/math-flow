from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT / "protocol/experiments/no-three-v10-v2-shadow-v1/manifest.json"
)
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")


def _sha256_path_content_v1(directory: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in directory.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(directory).as_posix()
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest.encode("ascii"))
        digest.update(b"\n")
    return f"sha256:{digest.hexdigest()}"


class NoThreeV10V2ShadowPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_current_contract_is_provider_free_and_fail_closed(self) -> None:
        manifest = self.manifest
        self.assertEqual(manifest["status"], "planned-unpublished-experiment")
        self.assertTrue(manifest["publicationForbidden"])
        self.assertTrue(manifest["productionMutationForbidden"])
        self.assertFalse(manifest["execution"]["providerExecutionAuthorized"])
        self.assertEqual(
            manifest["execution"]["adapter"],
            "provider-free-input-binding-audit-v1",
        )
        self.assertFalse(manifest["execution"]["continue"])
        self.assertEqual(manifest["execution"]["semanticFixtures"], [])
        self.assertEqual(manifest["execution"]["semanticOutputDigests"], [])
        self.assertEqual(
            manifest["execution"]["initialKnowledgeStateFactory"],
            "math_flow.research_builder_v7.empty_research_program_state_v3",
        )
        self.assertEqual(
            manifest["execution"]["initialAccountingStateFactory"],
            "math_flow.work_accounting.make_zero_work_accounting_state",
        )
        self.assertTrue(all(value == 0 for value in manifest["budgets"].values()))

        blockers = {
            blocker["id"]: blocker["status"]
            for blocker in manifest["blockingPrerequisites"]
        }
        self.assertEqual(
            blockers,
            {
                "experiment-scoped-root-contract": "missing",
                "real-evidence-shadow-runner": "missing",
                "explicit-provider-authorization": "missing",
            },
        )

    def test_local_protocol_inputs_are_exactly_digest_bound(self) -> None:
        expected_ids = {
            "knowledge-builder-spec",
            "work-accounting-spec",
            "work-accounting-policy",
        }
        observed_ids: set[str] = set()
        for frozen in self.manifest["frozenLocalInputs"]:
            observed_ids.add(frozen["id"])
            path = ROOT / frozen["path"]
            self.assertTrue(path.is_file(), frozen["path"])
            actual = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
            self.assertEqual(actual, frozen["digest"])
        self.assertEqual(observed_ids, expected_ids)

    def test_subjects_are_the_four_active_canonical_v4_acceptances(self) -> None:
        subjects = self.manifest["subjects"]
        self.assertEqual(len(subjects), 4)
        self.assertEqual(
            [subject["acceptedSequenceIndex"] for subject in subjects],
            [1, 2, 3, 4],
        )
        self.assertEqual(
            [subject["ledgerPosition"] for subject in subjects], [4, 5, 9, 10]
        )
        self.assertEqual(
            [subject["transactionId"] for subject in subjects],
            [
                "29ccbd396781fd36d436ed2e6d0952a4730361b9",
                "0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0",
                "87f78eb20d47a1db7d4ef35702bf00b4af94ad8d",
                "17928a941d7503ff0dc32740b707f475728300a3",
            ],
        )
        self.assertEqual(
            self.manifest["subjectSelection"]["acceptedCount"], len(subjects)
        )
        self.assertEqual(
            self.manifest["subjectSelection"]["canonicalContributionCount"], 10
        )
        self.assertEqual(self.manifest["subjectSelection"]["indeterminateCount"], 6)
        self.assertEqual(self.manifest["subjectSelection"]["invalidCount"], 0)

        contribution_root = ROOT / "problems/no-three-in-line-77/contributions"
        self.assertEqual(
            len([path for path in contribution_root.iterdir() if path.is_dir()]), 10
        )
        registry = json.loads(
            (ROOT / "protocol/problem-registry.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("no-three-in-line-77", registry["archivedProblems"])

    def test_subject_evidence_and_validity_bindings_are_complete(self) -> None:
        seen_transactions: set[str] = set()
        seen_judgments: set[str] = set()
        for subject in self.manifest["subjects"]:
            transaction = subject["transactionId"]
            judgment = subject["judgment"]
            self.assertRegex(transaction, GIT_OBJECT)
            self.assertNotIn(transaction, seen_transactions)
            seen_transactions.add(transaction)
            self.assertRegex(subject["gitTreeObjectId"], GIT_OBJECT)
            self.assertTrue(
                subject["claimKey"].startswith("no-three-in-line-77/")
            )
            self.assertEqual(subject["requiredDependencyTransactionIds"], [])

            contribution = ROOT / subject["contributionPath"]
            self.assertTrue(contribution.is_dir(), subject["contributionPath"])
            files = sorted(path for path in contribution.rglob("*") if path.is_file())
            evidence = subject["evidenceBundle"]
            self.assertEqual(evidence["algorithm"], "sha256-path-content-v1")
            self.assertEqual(evidence["fileCount"], len(files))
            self.assertEqual(evidence["bytes"], sum(path.stat().st_size for path in files))
            self.assertEqual(evidence["digest"], _sha256_path_content_v1(contribution))

            self.assertRegex(judgment["runDigest"], DIGEST)
            self.assertRegex(judgment["judgmentId"], DIGEST)
            self.assertNotIn(judgment["judgmentId"], seen_judgments)
            seen_judgments.add(judgment["judgmentId"])
            for field in (
                "judgmentRecordArtifactDigest",
                "dependencyPacketArtifactDigest",
                "dependencyPacketDigest",
                "reportArtifactDigest",
            ):
                self.assertRegex(judgment[field], DIGEST)
            for attestation in judgment["objectiveAttestationRunDigests"]:
                self.assertRegex(attestation, DIGEST)
            run_hex = judgment["runDigest"].removeprefix("sha256:")
            self.assertTrue(judgment["path"].endswith(run_hex))
            self.assertIn(f"/{run_hex[:2]}/", judgment["path"])

    def test_projection_snapshot_and_baselines_are_immutable_observations(self) -> None:
        snapshot = self.manifest["projectionSnapshot"]
        self.assertRegex(snapshot["commit"], GIT_OBJECT)
        self.assertRegex(snapshot["problemLedgerHead"], GIT_OBJECT)
        self.assertRegex(snapshot["problemLedgerDigest"], DIGEST)
        self.assertRegex(snapshot["catalog"]["digest"], DIGEST)
        self.assertRegex(snapshot["problemRunIndex"]["digest"], DIGEST)

        knowledge = self.manifest["observationalBaselines"]["legacyKnowledge"]
        self.assertEqual(knowledge["role"], "observational-relational-reference-not-gold")
        self.assertEqual(
            knowledge["counts"],
            {"programs": 4, "threads": 11, "items": 9, "contributions": 4},
        )
        self.assertEqual(
            knowledge["nonRootProgramIds"],
            [
                "certified-configurations",
                "rotational-symmetry",
                "rotational-symmetry/rct4",
            ],
        )
        self.assertEqual(sum(knowledge["itemTypeCounts"].values()), 9)

        credit = self.manifest["observationalBaselines"][
            "legacyHierarchicalCredit"
        ]
        self.assertEqual(
            credit["role"],
            "observational-topology-consumer-not-v2-work-accounting-oracle",
        )
        self.assertFalse(credit["comparableToWorkAccountingV2"])
        self.assertEqual(credit["programEvaluationCount"], 4)

    def test_future_envelope_is_bounded_but_not_authorization(self) -> None:
        envelope = self.manifest["futureExecutionEnvelope"]
        self.assertTrue(envelope["advisoryNotAuthorization"])
        self.assertEqual(envelope["nominalProviderCalls"], 4 * 6)
        self.assertEqual(envelope["maximumProviderCalls"], 4 * 6 * 3)
        v10_completion = 6000 + 4000 + 16000
        v2_completion = 12000 + 16000 + 16000
        self.assertEqual(
            envelope["maximumReservedCompletionTokens"],
            4 * 3 * (v10_completion + v2_completion),
        )
        self.assertTrue(envelope["requestSideVerifiedPriceBoundRequired"])
        self.assertTrue(envelope["stopOnFirstHardFailure"])
        self.assertTrue(envelope["stopOnProtocolConcernBeforeNextSubject"])
        self.assertTrue(envelope["blindRetryOutsideGovernedPolicyForbidden"])


if __name__ == "__main__":
    unittest.main()
