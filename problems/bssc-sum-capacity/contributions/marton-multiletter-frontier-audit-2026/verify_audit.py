#!/usr/bin/env python3
"""Deterministic structural and arithmetic audit for this contribution.

This checker intentionally does not contact arXiv or GitHub and does not execute
the external reproduction package.  It checks only locally encoded facts:
the BSSC matrices and reflection, the encoded superadditivity reduction, the
exact threshold closed form and its decimal displays, immutable source
metadata, replay-result consistency, and the declared evidence boundary.
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict:
    with (ROOT / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_matrix(raw: list[list[str]]) -> list[list[Fraction]]:
    return [[Fraction(entry) for entry in row] for row in raw]


def binary_entropy(value: Decimal) -> Decimal:
    """Return binary entropy using the active decimal context."""
    zero = Decimal(0)
    one = Decimal(1)
    if value in (zero, one):
        return zero
    return -(
        value * value.ln() + (one - value) * (one - value).ln()
    ) / Decimal(2).ln()


def check_bssc(spec: dict) -> None:
    bssc = spec["bssc"]
    assert bssc["inputAlphabet"] == [0, 1]
    y = parse_matrix(bssc["receiverY"])
    z = parse_matrix(bssc["receiverZ"])
    assert len(y) == len(z) == 2
    assert all(len(row) == 2 for row in y + z)
    assert all(entry >= 0 for row in y + z for entry in row)
    assert all(sum(row) == 1 for row in y + z)
    for x in range(2):
        for out in range(2):
            assert z[x][out] == y[1 - x][1 - out]
    assert any(entry == 0 for row in y + z for entry in row)
    assert bssc["reflectionRule"] == "P_Z(z|x)=P_Y(1-z|1-x)"


def check_threshold(spec: dict) -> None:
    direction = spec["directionAlignment"]
    assert direction["directionId"] == "bssc-multiletter-marton-frontier"
    assert direction["registrationTransactionId"] == "7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8"
    assert re.fullmatch(r"[0-9a-f]{40}", direction["registrationTransactionId"])
    assert "not a logical claim dependency" in direction["role"]
    rtd = spec["randomizedTimeDivision"]
    threshold = spec["improvementThreshold"]
    assert spec["units"] == "bits"
    assert rtd["receiverCurve"] == "J(q)=h_2(q/2)-q"
    assert rtd["differenceCurve"] == "D(q)=J(q)-J(1-q)"
    assert rtd["derivative"] == "D'(q)=(1/2) log_2(((2-q)(1+q))/(q(1-q)))-2"
    assert rtd["stationaryPolynomial"] == "15q^2-15q+2=0"
    assert rtd["globalMaximizer"] == "q_-=(15-sqrt(105))/30"
    assert rtd["exactClosedForm"] == (
        "L_RTD=h_2(1/4)-1/2+(1/2)"
        "[h_2(q_-/2)-h_2((1-q_-)/2)+1-2q_-]"
    )
    assert rtd["oneLetterIdentification"] == "M_1(P)=L_RTD"
    assert threshold["general"] == "S_n>n L_RTD"
    assert threshold["twoLetterExact"] == "S_2>2 L_RTD"
    assert "prefix" in rtd["prefixStatus"]
    assert "directed upper enclosure" in threshold["strictComparisonRequirement"]

    one = rtd["canonicalDecimalPrefix"]
    two = threshold["twoLetterDecimalPrefix"]
    assert re.fullmatch(r"0\.[0-9]+", one)
    assert re.fullmatch(r"0\.[0-9]+", two)
    assert len(one.partition(".")[2]) == 33
    assert len(two.partition(".")[2]) == 33
    with localcontext() as context:
        context.prec = 100
        decimal_one = Decimal(1)
        decimal_two = Decimal(2)
        decimal_fifteen = Decimal(15)
        q_minus = (decimal_fifteen - Decimal(105).sqrt()) / Decimal(30)
        q_plus = (decimal_fifteen + Decimal(105).sqrt()) / Decimal(30)

        def stationary_polynomial(value):
            return 15 * value * value - 15 * value + 2

        assert Decimal(0) < q_minus < Decimal("0.5") < q_plus < decimal_one
        assert abs(stationary_polynomial(q_minus)) < Decimal("1e-95")
        assert abs(stationary_polynomial(q_plus)) < Decimal("1e-95")

        # Exact-rational samples verify the quadratic sign pattern on the
        # four intervals separated by q_-, 1/2, and q_+.
        assert stationary_polynomial(Fraction(1, 10)) > 0
        assert stationary_polynomial(Fraction(1, 4)) < 0
        assert stationary_polynomial(Fraction(3, 4)) < 0
        assert stationary_polynomial(Fraction(9, 10)) > 0

        half = decimal_one / decimal_two
        quarter = decimal_one / Decimal(4)
        exact_value = (
            binary_entropy(quarter)
            - half
            + half
            * (
                binary_entropy(q_minus / decimal_two)
                - binary_entropy((decimal_one - q_minus) / decimal_two)
                + decimal_one
                - decimal_two * q_minus
            )
        )
        assert format(q_minus, "f").startswith(
            "0.158434974468013387225965377315964933"
        )
        assert format(exact_value, "f").startswith(one)
        assert format(decimal_two * exact_value, "f").startswith(two)
        assert Decimal(two) == decimal_two * Decimal(one)


def check_multiletter_structure(spec: dict) -> None:
    structure = spec["multiletterStructure"]
    assert structure["superadditivity"] == "M_{m+n}(P)>=M_m(P)+M_n(P)"
    assert structure["binaryOutputLinearBound"] == "0<=M_n(P)<=2n bits"
    assert structure["feketeLimit"] == (
        "lim_{n->infinity} M_n(P)/n=sup_{n>=1} M_n(P)/n"
    )
    assert structure["capacityLowerBound"] == (
        "C_sum(P)>=lim_{n->infinity} M_n(P)/n"
    )
    assert structure["witnessPropagation"] == (
        "an n-letter witness of value S_n yields a kn-letter witness of value k S_n"
    )

    # Exact-rational regression for the sole inequality in the concatenation
    # proof.  The README gives its universal elementary proof; this finite grid
    # guards the locally encoded direction and repeated-witness equality.
    samples = tuple(Fraction(value, 2) for value in range(5))
    for a_m in samples:
        for b_m in samples:
            for a_n in samples:
                for b_n in samples:
                    assert min(a_m + a_n, b_m + b_n) >= (
                        min(a_m, b_m) + min(a_n, b_n)
                    )
    for scale in range(1, 8):
        for a in samples:
            for b in samples:
                assert min(scale * a, scale * b) == scale * min(a, b)


def check_sources(manifest: dict) -> None:
    assert manifest["schemaVersion"] == 1
    assert manifest["auditDateUtc"] == "2026-08-22"
    sources = {source["arxivId"]: source for source in manifest["sources"]}
    assert set(sources) == {"2608.19869", "2608.13170"}

    expected = {
        "2608.19869": {
            "version": "v1",
            "submitted": "2026-08-20T10:27:59Z",
            "bytes": 285442,
            "sha256": "0c67e0b283be1b61c72cfff3c1870cf73f06233ea33bafeb5c6fc5b2a4f1ceca",
            "theorems": {4, 5},
        },
        "2608.13170": {
            "version": "v1",
            "submitted": "2026-08-13T12:39:09Z",
            "bytes": 324615,
            "sha256": "313c49fab92c69efb108d706101a3357276e88097e378083272c573a37f11c92",
            "theorems": {1, 2},
        },
    }
    for arxiv_id, want in expected.items():
        source = sources[arxiv_id]
        assert source["version"] == want["version"]
        assert source["submittedAtUtc"] == want["submitted"]
        assert source["abstractUrl"] == f"https://arxiv.org/abs/{arxiv_id}v1"
        assert source["htmlUrl"] == f"https://arxiv.org/html/{arxiv_id}v1"
        assert source["pdfUrl"] == f"https://arxiv.org/pdf/{arxiv_id}v1"
        assert source["downloadedPdf"]["bytes"] == want["bytes"]
        digest = source["downloadedPdf"]["sha256"]
        assert digest == want["sha256"]
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
        assert {item["number"] for item in source["declaredTheoremScope"]} == want["theorems"]
        assert source["statusInThisContribution"].endswith("not independently reproved")

    marton = sources["2608.19869"]
    input_scope = marton["inputAlphabetScope"]
    assert input_scope["certifiedBaseExample"] == "ternary input {0,1,2}"
    assert input_scope["explicitLiftCardinality"] == "3*2^2000000"
    assert "not proved" in input_scope["binaryInputStatus"]
    lift_gap = marton["reportedExplicitLiftGapNats"]
    assert Decimal(lift_gap["strictLowerBound"]) > 0
    assert Decimal(lift_gap["intervalReplay"][0]) > 0
    assert Decimal(lift_gap["intervalReplay"][0]) <= Decimal(lift_gap["intervalReplay"][1])

    markovity = sources["2608.13170"]["counterexampleScope"]
    assert markovity["input"] == markovity["outputs"] == "ternary"
    assert markovity["transitionProbabilities"] == "strictly positive"
    assert markovity["auxiliaryPattern"] == "nonrectangular 2x2"
    assert Decimal(markovity["secondCertifiedSeparationNatsAtLeast"]) > 0
    assert markovity["additivityStatus"] == "not resolved"


def check_replay(replay: dict) -> None:
    assert replay["schemaVersion"] == 1
    assert "do not independently prove" in replay["evidenceBoundary"]
    repository = replay["repository"]
    commit = repository["pinnedCommit"]
    assert commit == "cc33e854cb1c5e99cb18fe500f60a529fce136f8"
    assert re.fullmatch(r"[0-9a-f]{40}", commit)
    assert repository["immutableTreeUrl"].endswith("/tree/" + commit)
    assert repository["commitCountAtAudit"] == 1

    runs = {run["command"]: run for run in replay["runs"]}
    assert len(runs) == 4
    assert all(run["result"] == "PASS" for run in runs.values())
    manifest_run = runs[
        "PYTHONDONTWRITEBYTECODE=1 python3 src/portable/verify_saved_certificate_manifest.py"
    ]["observations"]
    assert manifest_run["deterministicMapsCovered"] == 3**4 == 81
    assert manifest_run["oneSidedBranchesCovered"] == ["U=X", "V=X"]
    assert manifest_run["processedBoxes"] == 4729704
    assert Decimal(manifest_run["storedFixedInputMargin"]) > 0

    lift_run = runs["bash scripts/run_lift_mpfr.sh"]["observations"]
    assert lift_run["precisionBits"] == 320
    lower, upper = map(Decimal, lift_run["gapIntervalNats"])
    assert Decimal(0) < lower <= upper
    one_upper = Decimal(lift_run["oneLetterUpperIntervalNats"][1])
    two_lower = Decimal(lift_run["twoLetterLowerIntervalNats"][0])
    # The one- and two-letter endpoints are short printed displays, whereas
    # the gap endpoint carries more digits and is evaluated directly by the
    # MPFR program.  Check display compatibility, not false exact equality.
    assert abs((two_lower - 2 * one_upper) - lower) < Decimal("1e-15")

    caveat = replay["repositoryCaveat"]
    assert caveat["absentManifestPaths"] == [
        ".gitignore",
        "paper/main.tex",
        "paper/paper.pdf",
    ]
    assert "every present path reports OK" in caveat["cleanCheckoutResult"]
    assert "cannot complete" in caveat["quickScriptConsequence"]
    assert "MPFR 4.2.1" in caveat["replayMutation"]
    assert "MPFR 4.2.2" in caveat["replayMutation"]
    assert "declared external results" in caveat["validitySeparation"]
    assert "rather than independently reproved" in caveat["validitySeparation"]


def check_claims(claims: dict) -> None:
    assert claims["schemaVersion"] == 1
    assert len(claims["claims"]) == 1
    claim = claims["claims"][0]
    assert claim["claimKey"] == "bssc-sum-capacity/marton-multiletter-frontier-audit-2026"
    assert claim["dependencyTransactionIds"] == []
    statement = claim["statement"]
    for required in (
        "C_sum(P) >= M_n(P)/n",
        "M_{m+n}(P) >= M_m(P)+M_n(P)",
        "lim_{n->infinity} M_n(P)/n",
        "k independent copies",
        "S_n > n L_RTD",
        "not a capacity converse",
        "directed upper enclosure",
    ):
        assert required in statement


def check_local_hashes() -> None:
    # A stable fingerprint is printed for reviewers; no expected digest is
    # self-embedded because changing the audited JSON should remain possible.
    for name in ("claims.json", "threshold_spec.json", "source_manifest.json", "replay_evidence.json"):
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
        print(f"{name}: sha256:{digest}")


def main() -> None:
    spec = load("threshold_spec.json")
    assert spec["schemaVersion"] == 1
    check_bssc(spec)
    check_threshold(spec)
    check_multiletter_structure(spec)
    check_sources(load("source_manifest.json"))
    check_replay(load("replay_evidence.json"))
    check_claims(load("claims.json"))
    check_local_hashes()
    print(
        "PASS: BSSC multiletter structure, exact threshold, source-scope, "
        "and replay-boundary audit is internally consistent."
    )


if __name__ == "__main__":
    main()
