#!/usr/bin/env python3
"""Fail-closed audit of the frozen finite BSSC search ledger."""

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
getcontext().prec = 80
D = Decimal


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = json.loads((ROOT / "evidence.json").read_text())
    require(evidence["schemaVersion"] == 1, "bad evidence schema")
    boundary = evidence["evidenceBoundary"].lower()
    require("directed enclosure" in boundary and "global optimality" in boundary,
            "missing evidence boundary")

    for name, expected in evidence["searchSourceSha256"].items():
        actual = digest(ROOT / "search" / name)
        require(actual == expected, ("search-source digest", name, actual, expected))

    threshold_record = evidence["threshold"]
    threshold_lower = D(threshold_record["directedLowerBits"])
    threshold_upper = D(threshold_record["directedUpperBits"])
    display_prefix = threshold_record["exactDisplayPrefixBits"]
    tolerance = D(threshold_record["declaredNoFindingToleranceBits"])
    require(threshold_lower < threshold_upper, "directed threshold ordering")
    require(threshold_record["directedLowerBits"].startswith(display_prefix)
            and threshold_record["directedUpperBits"].startswith(display_prefix),
            "display prefix not bound to directed interval")
    require(threshold_upper - threshold_lower < D("1e-68"),
            "directed threshold interval unexpectedly wide")
    require(threshold_record["certificateTransactionId"]
            == "88a1004f309460f3ec1cacdae88d30f88559f9bc",
            "threshold certificate transaction")
    require(evidence["sourceData"]["provenanceTransactionId"]
            == "f6ea30479b9ca461294ba89a8a1a31c06ce59d08",
            "external-source provenance transaction")

    transplant = evidence["transplant"]
    require(transplant["mapsPerLaw"] == 4 ** 9, "map count")
    require(transplant["totalLawMapEvaluations"]
            == transplant["componentLaws"] * transplant["mapsPerLaw"],
            "transplant coverage")
    map_id = sum(value * 4 ** j for j, value in enumerate(transplant["bestMap"]))
    require(map_id == transplant["bestMapId"], "base-4 map id")
    endpoints = [D(x) for x in transplant["bestEndpointsBits"]]
    require(abs(sum(endpoints) / D(2) - D(transplant["bestLHalfBits"]))
            <= D("2e-16"), "transplant endpoint average")
    require(D(transplant["maximumSeparableEitherOrientationBits"])
            < D(transplant["bestLHalfBits"]), "separable comparison")
    orientation_rows = transplant["separableOrientationMaximaBySourceRow"]
    require([row["sourceRow"] for row in orientation_rows] == [6, 7],
            "separable source rows")
    orientation_values = []
    for row in orientation_rows:
        orientation_values.extend([
            D(row["firstBitRowSecondBitColumnBits"]),
            D(row["firstBitColumnSecondBitRowBits"]),
        ])
    require(max(orientation_values)
            == D(transplant["maximumSeparableEitherOrientationBits"]),
            "separable union maximum")
    require(D(transplant["fairReflectedBalancedEndpointBits"]) < threshold_lower,
            "reflected transplant comparison")

    exact = evidence["exactTransplantAudit"]
    for label in ("raw", "fairReflected"):
        law = exact[label]
        y = D(law["yEndpointBits"])
        z = D(law["zEndpointBits"])
        half = D(law["lHalfBits"])
        require(abs((y + z) / D(2) - half) < D("1e-74"),
                ("exact endpoint average", label))
        left = D(law["residualLeftBits"])
        right = D(law["residualRightBits"])
        delta = D(law["residualDeltaBits"])
        require(abs(left - right - delta) < D("2e-75"),
                ("correlation residual", label))
        require(abs(D(law["identityResidualBits"])) <= D("5e-100"),
                ("identity residual", label))
    require(any(D(x) < 0 for x in exact["raw"]["paddingSlacksBits"]),
            "raw padding screen should reject")
    require(all(D(x) > 0 for x in exact["fairReflected"]["paddingSlacksBits"]),
            "reflected padding screens should all pass")
    float_exact_lhalf = (D(transplant["bestLHalfBits"])
                         - D(exact["raw"]["lHalfBits"]))
    float_exact_endpoints = [
        D(transplant["bestEndpointsBits"][0])
        - D(exact["raw"]["yEndpointBits"]),
        D(transplant["bestEndpointsBits"][1])
        - D(exact["raw"]["zEndpointBits"]),
    ]
    require(abs(float_exact_lhalf) < D("2e-15"),
            "float/exact transplant Lhalf")
    require(max(abs(x) for x in float_exact_endpoints) < D("2e-15"),
            "float/exact transplant endpoints")

    w4 = evidence["fullJointW4"]
    w8 = evidence["fullJointW8"]
    require(w4["starts"] * w4["iterationsPerStart"] == 960000,
            "W4 iteration coverage")
    require(w8["starts"] * w8["iterationsPerStart"] == 720000,
            "W8 iteration coverage")
    for campaign in (w4, w8):
        formula = campaign["seedFormula"]
        first, last = formula["indices"]
        require(first == 0, "seed range start")
        require(formula["base"] + formula["stride"] * last > formula["base"],
                "seed range end")

    continuation = evidence["transplantContinuation"]
    require(continuation["runsPerFamily"] * len(continuation["families"]) == 48,
            "continuation coverage")
    require(D(continuation["bestRawBits"])
            < D(continuation["bestReflectedBits"]), "reflection comparison")

    homotopy = evidence["homotopy"]
    nweights = len(homotopy["weights"])
    require(nweights == 11, "homotopy grid")
    for family in ("chordBits", "forwardBits", "reverseBits"):
        require(len(homotopy[family]) == nweights, ("homotopy length", family))
    require(D(homotopy["forwardBits"][3]) < threshold_lower - D("1e-3"),
            "forward lower branch")
    require(D(homotopy["forwardBits"][4]) > threshold_lower - D("2e-8"),
            "forward jump")
    require(D(homotopy["reverseBits"][2]) > threshold_lower - D("3e-7"),
            "reverse product branch")
    require(D(homotopy["reverseBits"][1]) < threshold_lower - D("1e-3"),
            "reverse jump")

    fixed = evidence["fixedInput"]
    require(len(fixed["aValues"]) == len(fixed["bestBits"])
            == len(fixed["bestStart"]) == 15,
            "fixed-input grid")
    fixed_values = [D(x) for x in fixed["bestBits"]]
    maximum_index = max(range(len(fixed_values)), key=fixed_values.__getitem__)
    require(fixed["aValues"][maximum_index] == fixed["maximumA"] == "0.25",
            "fixed-input maximum location")
    require(fixed_values[maximum_index] == D(fixed["maximumBits"]),
            "fixed-input maximum value")
    require(len(fixed_values) * fixed["startsPerA"] == 90,
            "fixed-input run coverage")

    escape = evidence["escape"]
    per_weight = (escape["baseRunsPerWeight"]
                  + escape["orthogonalRunsPerWeight"]
                  + escape["mapMutationRunsPerWeight"]
                  + escape["w8RunsPerWeight"])
    require(len(escape["weights"]) * per_weight == escape["totalRuns"] == 78,
            "escape coverage")
    escape_endpoints = [D(x) for x in escape["bestEndpointsBits"]]
    require(abs(sum(escape_endpoints) / D(2) - D(escape["bestBits"]))
            <= D("5e-16"), "escape endpoint average")
    require(D(escape["minimumInputMassAcrossBatch"]) > 0,
            "escape full input support")
    comparison = D(evidence["threshold"]["binary64ComparisonBits"])
    require(abs(D(escape["bestBits"]) - comparison
                - D(escape["bestMarginVsBinary64ComparisonBits"]))
            <= D("2e-16"), "escape margin")

    face = evidence["threeFaceStress"]
    require(face["faces"] * face["randomLawsPerFace"] == 20000,
            "face random coverage")
    require(face["faces"] * face["localStartsPerFace"] == 48,
            "face optimization coverage")
    require(D(face["maximumViolationBits"]) < 0, "face sign")

    recorded_objectives = [
        D(transplant["bestLHalfBits"]),
        D(transplant["fairReflectedBalancedEndpointBits"]),
        D(w4["bestBits"]),
        D(w4["productSeedBits"]),
        D(w4["bestInteriorBits"]),
        D(w8["bestBits"]),
        D(w8["productSeedBits"]),
        D(w8["bestInteriorBits"]),
        D(continuation["bestRawBits"]),
        D(continuation["bestReflectedBits"]),
        D(fixed["maximumBits"]),
        D(escape["bestBits"]),
    ]
    for family in ("chordBits", "forwardBits", "reverseBits"):
        recorded_objectives.extend(D(x) for x in homotopy[family])
    overshoot = max(recorded_objectives) - threshold_lower
    require(overshoot <= tolerance, ("declared no-finding tolerance", overshoot))

    require(D(evidence["independentChecks"]
              ["analyticGradientFiniteDifferenceResidualNats"]) < D("1e-9"),
            "gradient residual")
    require(D(evidence["independentChecks"]
              ["maximumEndpointVsEntropyObjectiveResidualNats"]) < D("1e-14"),
            "objective implementation residual")

    print("PASS: frozen finite BSSC search ledger")
    print("transplant evaluations:", transplant["totalLawMapEvaluations"])
    print("local search runs:",
          w4["starts"] + w8["starts"] + 48 + 33 + 90 + escape["totalRuns"] + 48)
    print("directed threshold lower (bits):", threshold_lower)
    print("directed threshold upper (bits):", threshold_upper)
    print("largest conservative overshoot vs directed lower (bits):", overshoot)
    print("best nontrivial escape margin (bits):",
          escape["bestMarginVsBinary64ComparisonBits"])
    print("float minus 100-digit transplant Lhalf (bits):", float_exact_lhalf)
    print("float minus 100-digit transplant endpoints (bits):",
          float_exact_endpoints)
    print("evidence boundary:", evidence["evidenceBoundary"])


if __name__ == "__main__":
    main()
