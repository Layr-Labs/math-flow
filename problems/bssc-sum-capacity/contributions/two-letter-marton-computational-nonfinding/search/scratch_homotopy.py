#!/usr/bin/env python3
"""Homotopy between the reflected nonrectangular basin and product RTD."""

import argparse
import itertools
import numpy as np

from scratch_stochastic_marton import (
    LN2, MartonHalf, TARGET_NATS, projected_gradient_residual,
)
from scratch_transplant_opt import information_metrics, reflected_law


def replay_reflected_basin(obj):
    initial = reflected_law()
    uniform = np.full(initial.shape, 1.0 / initial.size)
    rng = np.random.default_rng(2029080600)
    p0 = 0.99 * initial + 0.01 * uniform
    theta = np.log(p0) + rng.normal(0.0, 1.07, size=initial.shape)
    return obj.optimize(theta, 30000, 0.06)[1]


def align_auxiliaries(source, target):
    permutations = list(itertools.permutations(range(4)))
    best = (-1.0, None, None)
    for pw in permutations:
        wlaw = source[np.asarray(pw)]
        for pu in permutations:
            wulaw = wlaw[:, np.asarray(pu)]
            for pv in permutations:
                candidate = wulaw[:, :, np.asarray(pv)]
                affinity = float(np.sum(np.sqrt(candidate * target)))
                if affinity > best[0]:
                    best = affinity, (pw, pu, pv), candidate.copy()
    return best


def optimize_from(obj, p, iterations, lr):
    uniform = np.full(p.shape, 1.0 / p.size)
    p0 = (1.0 - 1e-12) * p + 1e-12 * uniform
    theta = np.log(p0)
    return obj.optimize(theta, iterations, lr)[1]


def report(obj, family, nominal_product_weight, p):
    value = obj.value_grad(p)[0]
    px = np.sum(p, axis=(0, 1, 2))
    print("HOMOTOPY", family, "product_weight", nominal_product_weight,
          "bits", repr(value / LN2),
          "margin_bits", repr((value - TARGET_NATS) / LN2),
          "input", px.tolist(), "min_input_mass", float(np.min(px)),
          "stationarity", projected_gradient_residual(obj, p),
          "IUV_given_WX_bits", information_metrics(p)[0],
          "cross_use_MI_given_W_bits", information_metrics(p)[1],
          "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--iterations", type=int, default=15000)
    parser.add_argument("--lr", type=float, default=0.05)
    args = parser.parse_args()

    obj = MartonHalf()
    product = obj.product_rtd()
    basin = replay_reflected_basin(obj)
    affinity, permutations, basin = align_auxiliaries(basin, product)
    print("alignment_affinity", affinity, "permutations", permutations,
          "product_bits", obj.value_grad(product)[0] / LN2,
          "basin_bits", obj.value_grad(basin)[0] / LN2,
          "aligned_TV", 0.5 * float(np.sum(np.abs(basin - product))), flush=True)

    grid = np.linspace(0.0, 1.0, args.steps + 1)
    # Independent starts on the aligned chord.
    for weight in grid:
        start = (1.0 - weight) * basin + weight * product
        p = optimize_from(obj, start, args.iterations, args.lr)
        report(obj, "chord", float(weight), p)

    # Forward continuation, nudging the previous local optimum toward product.
    p = basin.copy()
    previous = 0.0
    for weight in grid:
        if weight > previous:
            mix = (weight - previous) / (1.0 - previous)
            p = (1.0 - mix) * p + mix * product
        p = optimize_from(obj, p, args.iterations, args.lr)
        report(obj, "forward", float(weight), p)
        previous = float(weight)

    # Reverse continuation, nudging the product optimum toward the basin.
    p = product.copy()
    previous = 1.0
    for weight in grid[::-1]:
        if weight < previous:
            mix = (previous - weight) / previous
            p = (1.0 - mix) * p + mix * basin
        p = optimize_from(obj, p, args.iterations, args.lr)
        report(obj, "reverse", float(weight), p)
        previous = float(weight)


if __name__ == "__main__":
    main()
