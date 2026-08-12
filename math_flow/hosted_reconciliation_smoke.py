from __future__ import annotations

import argparse
import json
from pathlib import Path

from .errors import MathFlowError
from .judgments import detect_conflicts, run_primary_judgment_bundle
from .judges import load_source


PROBLEM_ID = "no-three-in-line-77"
PRIMARY_JUDGE = Path("protocol/judges/openrouter-markdown-judgment-v1.json")
CLAIM_KEY = "no-three-in-line/d77-rct4-exhausts-centered-half-turn-class"

# These are deliberately fallible, deterministic primary judgments. They bind
# exact canonical contribution evidence to one controlled opposition without
# publishing either judgment or changing a knowledge lane. The real hosted
# model is used only for the reconciliation that follows.
SCENARIOS: dict[str, dict[str, str]] = {
    "record-152-certificate": {
        "stance": "supports",
        "claimKey": "no-three-in-line/d77-certified-interval-152-154",
        "summary": "The exact certificate and row bound support 152 <= D(77) <= 154.",
        "report": (
            "# Deterministic primary fixture\n\n"
            "The repository certificate and its exact verifier support the certified "
            "interval 152 <= D(77) <= 154.\n"
        ),
    },
    "record-152-local-rigidity": {
        "stance": "supports",
        "claimKey": "no-three-in-line/d77-local-rigidity-through-two-removals",
        "summary": "The exact computation supports local rigidity through removal depth two.",
        "report": (
            "# Deterministic primary fixture\n\n"
            "The exhaustive exact computation supports the stated local-rigidity result "
            "through removal depth two and makes no global optimality claim.\n"
        ),
    },
    "rct4-154-search-instance": {
        "stance": "supports",
        "claimKey": CLAIM_KEY,
        "summary": (
            "This fallible primary reads the rct4 construction as exhausting the centered "
            "half-turn class at cardinality 154."
        ),
        "report": (
            "# Fallible supporting primary fixture\n\n"
            "This deliberately fallible primary overreads the contribution's description "
            "of rct4 as the remaining rotational route. It accepts the proposition that "
            "the rct4 constraints exhaust every centered half-turn-invariant 154-point "
            "candidate. The contribution's own later scope qualifications make this a "
            "plausible adjudication error for a reconciliation smoke test, not canonical "
            "mathematical state.\n"
        ),
    },
    "finite-rotation-classification-proof": {
        "stance": "refutes",
        "claimKey": CLAIM_KEY,
        "summary": (
            "The proof distinguishes the full centered half-turn class from the strict rct4 "
            "subclass, refuting their equivalence."
        ),
        "report": (
            "# Refuting primary fixture\n\n"
            "The later proof establishes only that a rotationally symmetric 154-point set "
            "must be invariant under the half-turn about (38,38). It explicitly states that "
            "rct4 imposes additional partial quarter-turn regularity and is a strict subclass "
            "of the centered half-turn class. Therefore rct4 does not exhaust that class.\n"
        ),
    },
}


def _transport(
    transaction_id: str, scenario: dict[str, str]
):
    responses = iter(
        [
            {
                "id": f"fixture-report-{transaction_id}",
                "model": "fixture/deterministic-primary",
                "choices": [{"message": {"content": scenario["report"]}}],
            },
            {
                "id": f"fixture-extract-{transaction_id}",
                "model": "fixture/deterministic-primary",
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "findings": [
                                        {
                                            "claimKey": scenario["claimKey"],
                                            "stance": scenario["stance"],
                                            "summary": scenario["summary"],
                                            "subjectTransactionIds": [transaction_id],
                                            "evidenceTransactionIds": [transaction_id],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ],
            },
        ]
    )
    return lambda _: next(responses)


def prepare_fixture(
    root: Path, output_dir: Path, head: str = "HEAD"
) -> dict[str, object]:
    root = root.resolve()
    output_dir = output_dir.resolve()
    source = load_source(root, PROBLEM_ID, head)
    transactions = list(source["transactions"])
    observed = {str(item["contributionId"]) for item in transactions}
    expected = set(SCENARIOS)
    if observed != expected:
        difference = sorted(expected - observed or observed - expected)[0]
        raise MathFlowError(
            "hosted reconciliation fixture must be reviewed for the current ledger: "
            f"{difference}"
        )

    bundle_dirs: list[Path] = []
    preceding: list[str] = []
    for transaction in transactions:
        contribution_id = str(transaction["contributionId"])
        transaction_id = str(transaction["transactionId"])
        scenario = SCENARIOS[contribution_id]
        bundle_dir = output_dir / f"primary-{int(transaction['ordinal'])}"
        run_primary_judgment_bundle(
            root,
            PROBLEM_ID,
            root / PRIMARY_JUDGE,
            head,
            [transaction_id],
            bundle_dir,
            context_transaction_ids=preceding,
            transport=_transport(transaction_id, scenario),
        )
        bundle_dirs.append(bundle_dir)
        preceding.append(transaction_id)

    conflicts = detect_conflicts(bundle_dirs)
    if len(conflicts) != 1 or conflicts[0].get("claimKey") != CLAIM_KEY:
        raise MathFlowError("hosted reconciliation fixture did not derive its exact conflict")
    output_dir.mkdir(parents=True, exist_ok=True)
    conflicts_path = output_dir / "conflicts.json"
    conflicts_path.write_text(
        json.dumps({"schemaVersion": 1, "conflicts": conflicts}, indent=2) + "\n",
        encoding="utf-8",
    )
    plan: dict[str, object] = {
        "schemaVersion": 1,
        "fixtureOnly": True,
        "warning": (
            "Deterministic fallible primaries for a non-publishing hosted smoke test; "
            "not canonical judgments or mathematical state."
        ),
        "problemId": PROBLEM_ID,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "primaryBundlePaths": [str(path) for path in bundle_dirs],
        "conflictId": conflicts[0]["conflictId"],
        "claimKey": CLAIM_KEY,
    }
    (output_dir / "fixture-plan.json").write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8"
    )
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare deterministic primary inputs for hosted reconciliation smoke testing"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    plan = prepare_fixture(args.root, args.output_dir, args.head)
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
