#!/usr/bin/env python3
"""Independently verify four persisted BSSC Marton terminal candidates.

This checker uses only the Python standard library.  It hashes every source,
log, transcript, and candidate file; reconstructs every binary64 probability
from its hexadecimal encoding; and recomputes the Marton objective from the
mutual-information definition rather than the entropy-gradient implementation
used by the NumPy runner.
"""

from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parent
D = Decimal
LN2 = math.log(2.0)
DEPENDENCY = "88a1004f309460f3ec1cacdae88d30f88559f9bc"
CASES = {
    "w4-product": ([4, 6, 6, 4], 0, "product"),
    "w4-interior": ([4, 6, 6, 4], 12, "interior"),
    "w8-product": ([8, 6, 6, 4], 0, "product"),
    "w8-interior": ([8, 6, 6, 4], 12, "interior"),
}
BOUNDARY = (
    "Four deterministic binary64 terminal-candidate records only. "
    "No directed objective enclosure, optimizer-completeness claim, "
    "KKT certificate, global-optimality claim, Marton-additivity "
    "theorem, or capacity converse."
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def load(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def transition(receiver, input_symbol, output_symbol):
    x1, x2 = divmod(input_symbol, 2)
    o1, o2 = divmod(output_symbol, 2)

    def one(bit, output):
        if receiver == "Y":
            if bit == 0:
                return 0.5
            return 1.0 if output == 1 else 0.0
        if bit == 0:
            return 1.0 if output == 0 else 0.0
        return 0.5

    return one(x1, o1) * one(x2, o2)


def mutual_information(joint, rows, columns):
    row = [0.0] * rows
    column = [0.0] * columns
    for first in range(rows):
        for second in range(columns):
            probability = joint[first * columns + second]
            row[first] += probability
            column[second] += probability
    total = 0.0
    for first in range(rows):
        for second in range(columns):
            probability = joint[first * columns + second]
            if probability:
                total += probability * math.log(
                    probability / (row[first] * column[second])
                )
    return total


def conditional_mutual_information(joint, nw, na, nb):
    w = [0.0] * nw
    wa = [0.0] * (nw * na)
    wb = [0.0] * (nw * nb)
    for wi in range(nw):
        for ai in range(na):
            for bi in range(nb):
                probability = joint[(wi * na + ai) * nb + bi]
                w[wi] += probability
                wa[wi * na + ai] += probability
                wb[wi * nb + bi] += probability
    total = 0.0
    for wi in range(nw):
        for ai in range(na):
            for bi in range(nb):
                probability = joint[(wi * na + ai) * nb + bi]
                if probability:
                    total += probability * math.log(
                        probability
                        * w[wi]
                        / (wa[wi * na + ai] * wb[wi * nb + bi])
                    )
    return total


def recompute(probabilities, shape):
    nw, nu, nv, nx = shape
    need(nx == 4, "four super-inputs")
    wy = [0.0] * (nw * 4)
    wz = [0.0] * (nw * 4)
    wuy = [0.0] * (nw * nu * 4)
    wvz = [0.0] * (nw * nv * 4)
    wuv = [0.0] * (nw * nu * nv)
    input_law = [0.0] * 4

    def index(wi, ui, vi, xi):
        return ((wi * nu + ui) * nv + vi) * nx + xi

    for wi in range(nw):
        for ui in range(nu):
            for vi in range(nv):
                for xi in range(nx):
                    probability = probabilities[index(wi, ui, vi, xi)]
                    wuv[(wi * nu + ui) * nv + vi] += probability
                    input_law[xi] += probability
                    for output in range(4):
                        py = probability * transition("Y", xi, output)
                        pz = probability * transition("Z", xi, output)
                        wy[wi * 4 + output] += py
                        wz[wi * 4 + output] += pz
                        wuy[(wi * nu + ui) * 4 + output] += py
                        wvz[(wi * nv + vi) * 4 + output] += pz

    value = (
        0.5 * mutual_information(wy, nw, 4)
        + 0.5 * mutual_information(wz, nw, 4)
        + conditional_mutual_information(wuy, nw, nu, 4)
        + conditional_mutual_information(wvz, nw, nv, 4)
        - conditional_mutual_information(wuv, nw, nu, nv)
    )
    return value, input_law


def check_metadata(manifest):
    claims = load(ROOT / "claims.json")
    need(claims["schemaVersion"] == 1, "claims schema")
    need(len(claims["claims"]) == 1, "one claim")
    claim = claims["claims"][0]
    need(
        claim["claimKey"]
        == "bssc-sum-capacity/two-letter-marton-four-run-execution-attestation",
        "claim key",
    )
    need(claim["dependencyTransactionIds"] == [DEPENDENCY],
         "direct valid dependency only")
    statement = claim["statement"]
    for phrase in (
        "Exactly four",
        "seed indices 0 and 12",
        "complete terminally reported best p(w,u,v,x_1x_2) arrays",
        "44 unreplayed U=V=6 runs",
        "no U=V=8 run",
        "negative binary64 evidence only",
        "not a directed objective enclosure",
        "capacity converse",
    ):
        need(phrase in statement, f"claim scope: {phrase}")

    verification = load(ROOT / "verification.json")
    need(verification["schemaVersion"] == 1, "verification schema")
    need(verification["entrypoint"] == "verify.py", "entrypoint")
    need(verification["arguments"] == [], "no arguments")
    need(manifest["dependencyTransactionIds"] == [DEPENDENCY],
         "manifest dependency")
    need(manifest["evidenceBoundary"] == BOUNDARY, "evidence boundary")


def check_candidate(case_id, manifest_run, combined_record, lower):
    shape, seed_index, family = CASES[case_id]
    directory = ROOT / manifest_run["directory"]
    run_path = directory / "run.json"
    candidate_path = directory / "candidate.json"
    terminal_path = directory / "terminal.jsonl"

    need(sha256(run_path) == manifest_run["runSha256"],
         f"{case_id} run hash")
    need(sha256(candidate_path) == manifest_run["candidateSha256"],
         f"{case_id} candidate hash")
    need(sha256(terminal_path) == manifest_run["terminalSha256"],
         f"{case_id} terminal hash")
    run = load(run_path)
    candidate = load(candidate_path)
    need(run == combined_record, f"{case_id} combined log identity")
    need(run["caseId"] == candidate["caseId"] == case_id,
         f"{case_id} identity")
    need(run["candidateSha256"] == manifest_run["candidateSha256"],
         f"{case_id} candidate cross-hash")
    need(run["sourceSha256"] == manifest_run["_sourceSha256"],
         f"{case_id} source cross-hash")
    need(run["shape"] == candidate["shape"] == shape, f"{case_id} shape")
    cells = math.prod(shape)
    need(run["completeJointCells"] == cells, f"{case_id} cell count")
    need(len(candidate["probabilitiesHex"]) == cells,
         f"{case_id} complete candidate length")
    need(run["seedIndex"] == manifest_run["seedIndex"] == seed_index,
         f"{case_id} seed index")
    need(run["seed"] == 2026082201 + 104729 * seed_index,
         f"{case_id} seed formula")
    need(run["initializationClass"] == family,
         f"{case_id} initialization family")
    need(run["iterationsRequested"] == run["iterationsExecuted"]
         == manifest_run["iterationsExecuted"] == 30000,
         f"{case_id} executed iterations")
    need(1 <= run["bestIteration"] <= 30000, f"{case_id} best iteration")

    probabilities = [
        float.fromhex(value) for value in candidate["probabilitiesHex"]
    ]
    need(all(math.isfinite(value) and value >= 0.0
             for value in probabilities), f"{case_id} finite probabilities")
    probability_sum = math.fsum(probabilities)
    need(abs(probability_sum - 1.0) <= 4e-15,
         f"{case_id} simplex")
    stored_sum = float.fromhex(candidate["simplexSumHex"])
    need(abs(stored_sum - probability_sum) <= 4e-15,
         f"{case_id} stored simplex sum")
    stored_simplex_residual = float.fromhex(
        run["terminal"]["simplexResidualHex"]
    )
    need(abs(stored_simplex_residual - abs(stored_sum - 1.0)) <= 1e-18,
         f"{case_id} stored simplex residual")
    recomputed, input_law = recompute(probabilities, shape)
    candidate_independent = float.fromhex(
        candidate["objective"]["independentNatsHex"]
    )
    run_independent = float.fromhex(
        run["terminal"]["independentObjectiveNatsHex"]
    )
    primary = float.fromhex(candidate["objective"]["primaryNatsHex"])
    need(abs(recomputed - candidate_independent) <= 2e-14,
         f"{case_id} stdlib independent objective")
    need(candidate_independent == run_independent,
         f"{case_id} independent objective identity")
    need(
        primary == float.fromhex(run["terminal"]["objectiveNatsHex"]),
        f"{case_id} primary objective identity",
    )
    recorded_residual = float.fromhex(
        run["terminal"]["implementationResidualNatsHex"]
    )
    need(
        candidate["objective"]["absoluteResidualNatsHex"]
        == run["terminal"]["implementationResidualNatsHex"],
        f"{case_id} candidate residual identity",
    )
    need(abs(abs(primary - candidate_independent) - recorded_residual)
         <= 1e-18, f"{case_id} implementation residual")
    need(recorded_residual <= 2e-14,
         f"{case_id} implementation agreement")

    recorded_input = [
        float.fromhex(value) for value in candidate["inputLawHex"]
    ]
    need(len(recorded_input) == 4, f"{case_id} input length")
    need(max(abs(left - right)
             for left, right in zip(input_law, recorded_input)) <= 3e-15,
         f"{case_id} input recomputation")
    need(candidate["inputLawHex"] == run["terminal"]["inputLawHex"],
         f"{case_id} input log identity")

    bits = recomputed / LN2
    need(D(repr(bits)) < lower, f"{case_id} recomputed below threshold lower")
    need(
        run["terminal"]["objectiveBitsHex"] == manifest_run["objectiveBitsHex"],
        f"{case_id} objective manifest identity",
    )
    need(
        candidate["objective"]["primaryBitsHex"]
        == run["terminal"]["objectiveBitsHex"],
        f"{case_id} candidate bits identity",
    )
    need(abs(bits - float.fromhex(manifest_run["objectiveBitsHex"])) <= 3e-14,
         f"{case_id} objective bits agreement")

    finite = run["finiteDifference"]
    finite_residual = float.fromhex(finite["absoluteResidualHex"])
    need(finite["seed"] == 918273, f"{case_id} finite-difference seed")
    need(0.0 <= finite_residual <= 2e-6,
         f"{case_id} finite-difference residual")
    need(
        abs(
            abs(
                float.fromhex(finite["centeredDifferenceHex"])
                - float.fromhex(finite["analyticHex"])
            )
            - finite_residual
        )
        <= 1e-15,
        f"{case_id} finite-difference consistency",
    )
    need(float.fromhex(run["terminal"]["activeGradientSpreadNatsHex"]) >= 0.0,
         f"{case_id} active diagnostic")
    need(
        float.fromhex(run["terminal"]["inactiveGradientViolationNatsHex"])
        >= 0.0,
        f"{case_id} inactive diagnostic",
    )

    terminal = [
        json.loads(line)
        for line in terminal_path.read_text(encoding="utf-8").splitlines()
    ]
    need([event["event"] for event in terminal] == ["START", "RESULT", "END"],
         f"{case_id} terminal sequence")
    need(all(event["caseId"] == case_id for event in terminal),
         f"{case_id} terminal identity")
    need(terminal[0]["sourceSha256"] == run["sourceSha256"],
         f"{case_id} terminal source hash")
    need(terminal[0]["iterationsRequested"] == 30000,
         f"{case_id} terminal start")
    need(terminal[1]["runSha256"] == manifest_run["runSha256"],
         f"{case_id} terminal run hash")
    need(terminal[1]["candidateSha256"] == manifest_run["candidateSha256"],
         f"{case_id} terminal candidate hash")
    need(
        terminal[1]["objectiveBitsHex"]
        == run["terminal"]["objectiveBitsHex"],
        f"{case_id} terminal objective",
    )
    need(
        terminal[1]["implementationResidualNatsHex"]
        == run["terminal"]["implementationResidualNatsHex"],
        f"{case_id} terminal implementation residual",
    )
    need(terminal[1]["iterationsExecuted"] == 30000,
         f"{case_id} terminal completion")
    need(terminal[2]["status"] == "complete", f"{case_id} terminal status")
    return bits


def main():
    manifest = load(ROOT / "manifest.json")
    need(manifest["schemaVersion"] == 1, "manifest schema")
    check_metadata(manifest)
    need(manifest["source"]["sha256"] == sha256(ROOT / "run_case.py"),
         "runner source hash")
    need(
        manifest["manifestBuilder"]["sha256"]
        == sha256(ROOT / "build_manifest.py"),
        "manifest-builder hash",
    )
    run_log_path = ROOT / manifest["combinedRunLog"]["path"]
    need(sha256(run_log_path) == manifest["combinedRunLog"]["sha256"],
         "combined JSONL hash")
    combined = [
        json.loads(line)
        for line in run_log_path.read_text(encoding="utf-8").splitlines()
    ]
    need(len(combined) == manifest["combinedRunLog"]["records"] == 4,
         "four combined run records")
    need(len(manifest["runs"]) == 4, "four manifest runs")
    need([run["caseId"] for run in manifest["runs"]] == list(CASES),
         "exact case order")

    lower = D(manifest["threshold"]["directedLowerBits"])
    upper = D(manifest["threshold"]["directedUpperBits"])
    need(lower < upper and upper - lower < D("1e-69"),
         "directed threshold interval")
    values = []
    for manifest_run, combined_record in zip(manifest["runs"], combined):
        augmented = dict(manifest_run)
        augmented["_sourceSha256"] = manifest["source"]["sha256"]
        values.append(
            check_candidate(
                manifest_run["caseId"], augmented, combined_record, lower
            )
        )

    coverage = manifest["coverage"]
    need(coverage["caseIds"] == list(CASES), "coverage cases")
    need(coverage["runs"] == 4, "coverage run count")
    need(coverage["iterationsPerRun"] == 30000, "coverage iterations")
    need(coverage["optimizerSteps"] == 120000, "coverage steps")
    need(coverage["explicitlyDisavowedUnreplayedU6Runs"] == 44,
         "unreplayed U6 scope")
    need(coverage["includesAnyU8CardinalityRun"] is False,
         "no U=V=8 scope")
    need(coverage["includesAnyBroadPriorCampaign"] is False,
         "no broad-prior scope")

    print("PASS: four complete BSSC terminal candidates independently replayed")
    print("runner source sha256:", manifest["source"]["sha256"])
    print("combined JSONL sha256:", manifest["combinedRunLog"]["sha256"])
    for case_id, value in zip(CASES, values):
        print(case_id, "stdlib objective bits", repr(value))
    print("direct dependency:", DEPENDENCY)
    print("evidence boundary:", BOUNDARY)


if __name__ == "__main__":
    main()
