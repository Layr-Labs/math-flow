#!/usr/bin/env python3
"""Optimize a reflected BSSC law seeded by the 2026 nonrectangular witness."""

import argparse
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from scratch_stochastic_marton import (
    LN2, MartonHalf, TARGET_NATS, entropy, projected_gradient_residual,
)
from scratch_transplant_audit import audit


SOURCE = Path("/tmp/Suboptimality_Marton-audit-jdichc/data/certificates/"
              "fixed_input/cc_certificate_e5e-7.json")
SOURCE_SHA256 = "45502b2e7a694ae2d1beaee3e19249d63d9efe39b6405daa42ada0e1cbb846d6"
MAPPING = (1, 0, 3, 0, 0, 2, 3, 2, 3)


def source_law(row=7):
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise AssertionError((digest, SOURCE_SHA256))
    data = json.loads(SOURCE.read_text())
    record = next(r for r in data["winning_schemes"] if int(r["row_index"]) == row)
    denominator = int(record["probability_denominator"])
    source = (np.asarray(record["probability_numerators"], dtype=np.float64)
              .reshape(2, 4, 4, 9) / denominator)
    p = np.zeros((2, 4, 4, 4), dtype=np.float64)
    for old_x, new_x in enumerate(MAPPING):
        p[:, :, :, new_x] += source[:, :, :, old_x]
    return p


def reflected_law(row=7):
    base = source_law(row)
    p = np.zeros((4, 4, 4, 4), dtype=np.float64)
    p[:2] = 0.5 * base
    for w in range(2):
        for u in range(4):
            for v in range(4):
                for x in range(4):
                    p[2 + w, v, u, 3 - x] += 0.5 * base[w, u, v, x]
    return p


def information_metrics(p):
    # Non-Markovity of the satellites, I(U;V|W,X).
    wux = np.sum(p, axis=2)
    wvx = np.sum(p, axis=1)
    wx = np.sum(p, axis=(1, 2))
    i_uv_wx = entropy(wux) + entropy(wvx) - entropy(wx) - entropy(p)

    # Cross-use dependence after interpreting each U,V,X label as two bits:
    # I((U1,V1,X1);(U2,V2,X2)|W).
    nw = p.shape[0]
    w = np.sum(p, axis=(1, 2, 3))
    ws1 = np.zeros((nw, 8), dtype=np.float64)
    ws2 = np.zeros((nw, 8), dtype=np.float64)
    ws1s2 = np.zeros((nw, 8, 8), dtype=np.float64)
    for wi in range(nw):
        for u in range(4):
            u1, u2 = divmod(u, 2)
            for v in range(4):
                v1, v2 = divmod(v, 2)
                for x in range(4):
                    x1, x2 = divmod(x, 2)
                    s1 = 4 * u1 + 2 * v1 + x1
                    s2 = 4 * u2 + 2 * v2 + x2
                    mass = p[wi, u, v, x]
                    ws1[wi, s1] += mass
                    ws2[wi, s2] += mass
                    ws1s2[wi, s1, s2] += mass
    cross = entropy(ws1) + entropy(ws2) - entropy(w) - entropy(ws1s2)
    return i_uv_wx / LN2, cross / LN2


def exact_float_snapshot(p):
    flat = [F.from_float(float(value)) for value in p.ravel()]
    total = sum(flat, F(0))
    flat = [value / total for value in flat]
    nw = p.shape[0]
    out = [[[[F(0) for _ in range(4)] for _ in range(4)]
            for _ in range(4)] for _ in range(nw)]
    k = 0
    for w in range(nw):
        for u in range(4):
            for v in range(4):
                for x in range(4):
                    out[w][u][v][x] = flat[k]
                    k += 1
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=24)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--grid-size", type=int, default=None)
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--iterations", type=int, default=30000)
    parser.add_argument("--lr", type=float, default=0.06)
    args = parser.parse_args()

    initial = source_law() if args.raw else reflected_law()
    obj = MartonHalf(nw=initial.shape[0])
    initial_value = obj.value_grad(initial)[0]
    print("source", SOURCE, "sha256", SOURCE_SHA256,
          "row", 7, "mapping", MAPPING)
    print("shape", initial.shape,
          "initial_bits", initial_value / LN2,
          "initial_margin_bits", (initial_value - TARGET_NATS) / LN2,
          "initial_IUV_given_WX_bits", information_metrics(initial)[0],
          "initial_cross_use_MI_given_W_bits", information_metrics(initial)[1],
          "simplex_residual", abs(float(np.sum(initial)) - 1.0), flush=True)

    uniform = np.full(initial.shape, 1.0 / initial.size)
    best = (-math.inf, None, None)
    grid_size = args.grid_size if args.grid_size is not None else args.seeds
    for offset in range(args.seeds):
        i = args.start_index + offset
        seed = 2026082251 + 130363 * i
        rng = np.random.default_rng(seed)
        epsilon = 10.0 ** (-7.0 + 5.0 * i / max(1, grid_size - 1))
        p0 = (1.0 - epsilon) * initial + epsilon * uniform
        theta = np.log(p0) + rng.normal(0.0, 0.15 + 0.04 * i,
                                        size=initial.shape)
        value, p, best_it = obj.optimize(theta, args.iterations, args.lr)
        stationarity = projected_gradient_residual(obj, p)
        nonmarkov, crossuse = information_metrics(p)
        print("run", i, "seed", seed, "epsilon", epsilon,
              "bits", repr(value / LN2),
              "margin_bits", repr((value - TARGET_NATS) / LN2),
              "best_it", best_it, "stationarity", stationarity,
              "IUV_given_WX_bits", nonmarkov,
              "cross_use_MI_given_W_bits", crossuse,
              "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)
        if value > best[0]:
            best = value, p, seed
    value, p, seed = best
    print("FINAL seed", seed, "bits", repr(value / LN2),
          "margin_bits", repr((value - TARGET_NATS) / LN2),
          "input", np.sum(p, axis=(0, 1, 2)).tolist(),
          "stationarity", projected_gradient_residual(obj, p),
          "IUV_given_WX_bits", information_metrics(p)[0],
          "cross_use_MI_given_W_bits", information_metrics(p)[1],
          "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)
    label = "raw_optimized_float_snapshot" if args.raw else "reflected_optimized_float_snapshot"
    audit(label, exact_float_snapshot(p))


if __name__ == "__main__":
    main()
