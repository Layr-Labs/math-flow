#!/usr/bin/env python3
"""Build the immutable manifest for the four attested run directories."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASES = ("w4-product", "w4-interior", "w8-product", "w8-interior")
DEPENDENCY = "88a1004f309460f3ec1cacdae88d30f88559f9bc"
THRESHOLD_LOWER = (
    "0.7232857688439092313268831563011740144159620214477211104074274596056014"
)
THRESHOLD_UPPER = (
    "0.7232857688439092313268831563011740144159620214477211104074274596056016"
)


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    records = []
    manifest_runs = []
    source_hash = sha256(ROOT / "run_case.py")
    for case_id in CASES:
        directory = ROOT / "runs" / case_id
        run_path = directory / "run.json"
        candidate_path = directory / "candidate.json"
        terminal_path = directory / "terminal.jsonl"
        run = load(run_path)
        candidate = load(candidate_path)
        if run["caseId"] != case_id or candidate["caseId"] != case_id:
            raise AssertionError(f"case identity: {case_id}")
        if run["sourceSha256"] != source_hash:
            raise AssertionError(f"source hash: {case_id}")
        if run["candidateSha256"] != sha256(candidate_path):
            raise AssertionError(f"candidate hash: {case_id}")
        records.append(run)
        manifest_runs.append(
            {
                "caseId": case_id,
                "directory": f"runs/{case_id}",
                "runSha256": sha256(run_path),
                "candidateSha256": sha256(candidate_path),
                "terminalSha256": sha256(terminal_path),
                "objectiveBitsHex": run["terminal"]["objectiveBitsHex"],
                "iterationsExecuted": run["iterationsExecuted"],
                "seedIndex": run["seedIndex"],
            }
        )

    runs_jsonl = ROOT / "runs.jsonl"
    runs_jsonl.write_text(
        "\n".join(stable_json(record) for record in records) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schemaVersion": 1,
        "evidenceBoundary": (
            "Four deterministic binary64 terminal-candidate records only. "
            "No directed objective enclosure, optimizer-completeness claim, "
            "KKT certificate, global-optimality claim, Marton-additivity "
            "theorem, or capacity converse."
        ),
        "dependencyTransactionIds": [DEPENDENCY],
        "threshold": {
            "directedLowerBits": THRESHOLD_LOWER,
            "directedUpperBits": THRESHOLD_UPPER,
        },
        "source": {
            "path": "run_case.py",
            "sha256": source_hash,
        },
        "manifestBuilder": {
            "path": "build_manifest.py",
            "sha256": sha256(ROOT / "build_manifest.py"),
        },
        "combinedRunLog": {
            "path": "runs.jsonl",
            "sha256": sha256(runs_jsonl),
            "records": len(records),
        },
        "runs": manifest_runs,
        "coverage": {
            "caseIds": list(CASES),
            "runs": 4,
            "iterationsPerRun": 30000,
            "optimizerSteps": 120000,
            "explicitlyDisavowedUnreplayedU6Runs": 44,
            "includesAnyU8CardinalityRun": False,
            "includesAnyBroadPriorCampaign": False,
        },
    }
    (ROOT / "manifest.json").write_text(
        stable_json(manifest) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
