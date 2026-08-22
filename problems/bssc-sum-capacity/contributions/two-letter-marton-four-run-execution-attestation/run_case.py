#!/usr/bin/env python3
"""Execute and persist one deterministic BSSC Marton search case.

This discovery runner requires NumPy.  It writes a complete binary64 terminal
candidate as hexadecimal floats, a per-run JSON record, and a JSONL terminal
transcript.  Each named case writes to its own directory, so cases may run in
parallel without shared writable state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np


LN2 = math.log(2.0)
ONE_RTD_BITS = 0.361642884421954615663441578150587
TARGET_NATS = 2.0 * ONE_RTD_BITS * LN2
A_RTD = 0.1584349792600164
TOTAL_SEEDS = 24

CASES = {
    "w4-product": (4, 6, 6, 0),
    "w4-interior": (4, 6, 6, 12),
    "w8-product": (8, 6, 6, 0),
    "w8-interior": (8, 6, 6, 12),
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def product_channel(base):
    out = np.empty((4, 4), dtype=np.float64)
    for x in range(4):
        x1, x2 = divmod(x, 2)
        for y in range(4):
            y1, y2 = divmod(y, 2)
            out[x, y] = base[x1, y1] * base[x2, y2]
    return out


TY = product_channel(np.array([[0.5, 0.5], [0.0, 1.0]]))
TZ = product_channel(np.array([[1.0, 0.0], [0.5, 0.5]]))


def entropy(array):
    positive = array[array > 0.0]
    return -float(positive @ np.log(positive))


def softmax(theta):
    shifted = theta.ravel() - float(np.max(theta))
    exponential = np.exp(np.maximum(shifted, -745.0))
    return (exponential / float(np.sum(exponential))).reshape(theta.shape)


class MartonHalf:
    def __init__(self, nw, nu, nv):
        self.shape = (nw, nu, nv, 4)
        self.nw, self.nu, self.nv, self.nx = self.shape

    def value_grad(self, p):
        wy = np.einsum("wuvx,xy->wy", p, TY)
        wz = np.einsum("wuvx,xz->wz", p, TZ)
        wuy = np.einsum("wuvx,xy->wuy", p, TY)
        wvz = np.einsum("wuvx,xz->wvz", p, TZ)
        wuv = np.sum(p, axis=3)
        y = np.sum(wy, axis=0)
        z = np.sum(wz, axis=0)

        value = (
            0.5 * entropy(y)
            + 0.5 * entropy(z)
            + 0.5 * entropy(wy)
            + 0.5 * entropy(wz)
            - entropy(wuy)
            - entropy(wvz)
            + entropy(wuv)
        )

        tiny = np.finfo(np.float64).tiny
        ly = np.log(np.maximum(y, tiny)) + 1.0
        lz = np.log(np.maximum(z, tiny)) + 1.0
        lwy = np.log(np.maximum(wy, tiny)) + 1.0
        lwz = np.log(np.maximum(wz, tiny)) + 1.0
        lwuy = np.log(np.maximum(wuy, tiny)) + 1.0
        lwvz = np.log(np.maximum(wvz, tiny)) + 1.0
        lwuv = np.log(np.maximum(wuv, tiny)) + 1.0

        gx = -0.5 * (TY @ ly) - 0.5 * (TZ @ lz)
        gwy = -0.5 * np.einsum("xy,wy->wx", TY, lwy)
        gwz = -0.5 * np.einsum("xz,wz->wx", TZ, lwz)
        gwuy = np.einsum("xy,wuy->wux", TY, lwuy)
        gwvz = np.einsum("xz,wvz->wvx", TZ, lwvz)
        gradient = (
            gx[None, None, None, :]
            + gwy[:, None, None, :]
            + gwz[:, None, None, :]
            + gwuy[:, :, None, :]
            + gwvz[:, None, :, :]
            - lwuv[:, :, :, None]
        )
        return value, gradient

    def product_rtd(self):
        p = np.zeros(self.shape, dtype=np.float64)
        for w1 in range(2):
            for w2 in range(2):
                w = 2 * w1 + w2
                for x1 in range(2):
                    for x2 in range(2):
                        q1 = A_RTD if w1 == 0 else 1.0 - A_RTD
                        q2 = A_RTD if w2 == 0 else 1.0 - A_RTD
                        px1 = q1 if x1 == 0 else 1.0 - q1
                        px2 = q2 if x2 == 0 else 1.0 - q2
                        u = 2 * (x1 if w1 == 0 else 0) + (
                            x2 if w2 == 0 else 0
                        )
                        v = 2 * (x1 if w1 == 1 else 0) + (
                            x2 if w2 == 1 else 0
                        )
                        x = 2 * x1 + x2
                        p[w, u, v, x] += 0.25 * px1 * px2
        return p

    def finite_difference(self, seed=918273):
        rng = np.random.default_rng(seed)
        p = rng.random(self.shape)
        p /= np.sum(p)
        direction = rng.normal(size=self.shape)
        direction -= np.mean(direction)
        direction /= np.max(np.abs(direction))
        step = 0.01 * float(np.min(p))
        value, gradient = self.value_grad(p)
        finite = (
            self.value_grad(p + step * direction)[0]
            - self.value_grad(p - step * direction)[0]
        ) / (2.0 * step)
        analytic = float(np.sum(gradient * direction))
        return value, finite, analytic, abs(finite - analytic)

    def optimize(self, theta, iterations, rate):
        first = np.zeros(self.shape, dtype=np.float64)
        second = np.zeros(self.shape, dtype=np.float64)
        best_value = -math.inf
        best_p = None
        best_iteration = 0
        for iteration in range(1, iterations + 1):
            p = softmax(theta)
            value, gradient_p = self.value_grad(p)
            if value > best_value:
                best_value = value
                best_p = p.copy()
                best_iteration = iteration
            centered = gradient_p - float(np.sum(p * gradient_p))
            gradient_theta = p * centered
            first = 0.9 * first + 0.1 * gradient_theta
            second = 0.999 * second + 0.001 * gradient_theta * gradient_theta
            first_hat = first / (1.0 - 0.9**iteration)
            second_hat = second / (1.0 - 0.999**iteration)
            fraction = (iteration - 1.0) / max(1.0, iterations - 1.0)
            step = rate * (0.05 + 0.95 * (1.0 - fraction) ** 2)
            theta += step * first_hat / (np.sqrt(second_hat) + 1e-14)
            theta -= float(np.max(theta))
            np.maximum(theta, -90.0, out=theta)
        return best_value, best_p, best_iteration


def conditional_mutual_information(joint, axis_a, axis_b):
    # joint axes are (W,A,B); compute I(A;B|W) directly.
    need(joint.ndim == 3, "conditional-MI rank")
    w_marginal = np.sum(joint, axis=(axis_a, axis_b))
    wa = np.sum(joint, axis=axis_b)
    wb = np.sum(joint, axis=axis_a)
    total = 0.0
    for w in range(joint.shape[0]):
        for a in range(joint.shape[1]):
            for b in range(joint.shape[2]):
                probability = float(joint[w, a, b])
                if probability:
                    ratio = (
                        probability
                        * float(w_marginal[w])
                        / (float(wa[w, a]) * float(wb[w, b]))
                    )
                    total += probability * math.log(ratio)
    return total


def mutual_information(joint):
    row = np.sum(joint, axis=1)
    column = np.sum(joint, axis=0)
    total = 0.0
    for first in range(joint.shape[0]):
        for second in range(joint.shape[1]):
            probability = float(joint[first, second])
            if probability:
                total += probability * math.log(
                    probability / (float(row[first]) * float(column[second]))
                )
    return total


def independent_objective(p):
    wy = np.einsum("wuvx,xy->wy", p, TY)
    wz = np.einsum("wuvx,xz->wz", p, TZ)
    wuy = np.einsum("wuvx,xy->wuy", p, TY)
    wvz = np.einsum("wuvx,xz->wvz", p, TZ)
    wuv = np.sum(p, axis=3)
    return (
        0.5 * mutual_information(wy)
        + 0.5 * mutual_information(wz)
        + conditional_mutual_information(wuy, 1, 2)
        + conditional_mutual_information(wvz, 1, 2)
        - conditional_mutual_information(wuv, 1, 2)
    )


def projected_gradient_diagnostic(obj, p):
    _, gradient = obj.value_grad(p)
    active = p > 1e-10
    lam = float(np.sum(p[active] * gradient[active]) / np.sum(p[active]))
    spread = float(np.max(np.abs(gradient[active] - lam)))
    inactive = (
        float(np.max(gradient[~active] - lam)) if np.any(~active) else 0.0
    )
    return spread, max(0.0, inactive), int(np.sum(active))


def hex_list(array):
    return [float(value).hex() for value in array.ravel()]


def initialize(obj, seed_index):
    seed = 2026082201 + 104729 * seed_index
    rng = np.random.default_rng(seed)
    product = obj.product_rtd()
    uniform = np.full(obj.shape, 1.0 / np.prod(obj.shape))
    if seed_index < TOTAL_SEEDS // 2:
        epsilon = 10.0 ** (
            -8.0 + 6.0 * seed_index / (TOTAL_SEEDS // 2 - 1)
        )
        p0 = (1.0 - epsilon) * product + epsilon * uniform
        theta = np.log(p0) + rng.normal(
            0.0, 0.35 + 0.12 * seed_index, size=obj.shape
        )
        family = "product"
        initialization = {
            "epsilonHex": float(epsilon).hex(),
            "noiseStdHex": float(0.35 + 0.12 * seed_index).hex(),
        }
    else:
        theta = rng.normal(0.0, 1.5, size=obj.shape)
        family = "interior"
        initialization = {"noiseStdHex": float(1.5).hex()}
    return seed, family, initialization, theta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(CASES), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=30000)
    parser.add_argument("--lr", type=float, default=0.07)
    args = parser.parse_args()

    need(args.iterations == 30000, "attested iteration count")
    need(args.lr == 0.07, "attested initial rate")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    need(not any(args.output_dir.iterdir()), "output directory must be empty")

    source_hash = sha256(Path(__file__).resolve())
    nw, nu, nv, seed_index = CASES[args.case]
    obj = MartonHalf(nw, nu, nv)
    seed, family, initialization, theta = initialize(obj, seed_index)
    terminal = []

    def emit(event):
        line = stable_json(event)
        terminal.append(line)
        print(line, flush=True)

    emit(
        {
            "caseId": args.case,
            "event": "START",
            "iterationsRequested": args.iterations,
            "lrHex": float(args.lr).hex(),
            "seed": seed,
            "seedIndex": seed_index,
            "shape": list(obj.shape),
            "sourceSha256": source_hash,
        }
    )

    finite = obj.finite_difference()
    value, p, best_iteration = obj.optimize(theta, args.iterations, args.lr)
    independent = independent_objective(p)
    spread, inactive, active_count = projected_gradient_diagnostic(obj, p)
    input_law = np.sum(p, axis=(0, 1, 2))

    candidate = {
        "schemaVersion": 1,
        "caseId": args.case,
        "shape": list(obj.shape),
        "flattenOrder": "C order over (w,u,v,x)",
        "probabilitiesHex": hex_list(p),
        "objective": {
            "primaryNatsHex": float(value).hex(),
            "independentNatsHex": float(independent).hex(),
            "absoluteResidualNatsHex": float(abs(value - independent)).hex(),
            "primaryBitsHex": float(value / LN2).hex(),
        },
        "inputLawHex": hex_list(input_law),
        "simplexSumHex": float(np.sum(p)).hex(),
    }
    candidate_path = args.output_dir / "candidate.json"
    candidate_path.write_text(stable_json(candidate) + "\n", encoding="utf-8")
    candidate_hash = sha256(candidate_path)

    run = {
        "schemaVersion": 1,
        "caseId": args.case,
        "candidateFile": "candidate.json",
        "candidateSha256": candidate_hash,
        "sourceSha256": source_hash,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "shape": list(obj.shape),
        "completeJointCells": int(np.prod(obj.shape)),
        "seedFormula": "2026082201+104729*i",
        "seedIndex": seed_index,
        "seed": seed,
        "initializationClass": family,
        "initialization": initialization,
        "iterationsRequested": args.iterations,
        "iterationsExecuted": args.iterations,
        "bestIteration": best_iteration,
        "initialRateHex": float(args.lr).hex(),
        "finiteDifference": {
            "seed": 918273,
            "objectiveNatsHex": float(finite[0]).hex(),
            "centeredDifferenceHex": float(finite[1]).hex(),
            "analyticHex": float(finite[2]).hex(),
            "absoluteResidualHex": float(finite[3]).hex(),
        },
        "terminal": {
            "objectiveNatsHex": float(value).hex(),
            "objectiveBitsHex": float(value / LN2).hex(),
            "binary64TargetBitsHex": float(TARGET_NATS / LN2).hex(),
            "marginBitsHex": float((value - TARGET_NATS) / LN2).hex(),
            "independentObjectiveNatsHex": float(independent).hex(),
            "implementationResidualNatsHex": float(
                abs(value - independent)
            ).hex(),
            "activeThresholdHex": float(1e-10).hex(),
            "activeCells": active_count,
            "activeGradientSpreadNatsHex": float(spread).hex(),
            "inactiveGradientViolationNatsHex": float(inactive).hex(),
            "simplexResidualHex": float(abs(np.sum(p) - 1.0)).hex(),
            "inputLawHex": hex_list(input_law),
        },
    }
    run_path = args.output_dir / "run.json"
    run_path.write_text(stable_json(run) + "\n", encoding="utf-8")
    run_hash = sha256(run_path)

    emit(
        {
            "bestIteration": best_iteration,
            "candidateSha256": candidate_hash,
            "caseId": args.case,
            "event": "RESULT",
            "implementationResidualNatsHex": run["terminal"][
                "implementationResidualNatsHex"
            ],
            "iterationsExecuted": args.iterations,
            "objectiveBitsHex": run["terminal"]["objectiveBitsHex"],
            "runSha256": run_hash,
        }
    )
    emit(
        {
            "caseId": args.case,
            "event": "END",
            "status": "complete",
        }
    )
    terminal_path = args.output_dir / "terminal.jsonl"
    terminal_path.write_text("\n".join(terminal) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
