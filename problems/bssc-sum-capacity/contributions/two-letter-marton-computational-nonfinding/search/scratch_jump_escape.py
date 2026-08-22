#!/usr/bin/env python3
"""Orthogonal, map-mutation, and W=8 escape search near the homotopy jump."""

import argparse
import itertools
import math
import numpy as np

from scratch_stochastic_marton import (
    LN2, MartonHalf, TARGET_NATS, entropy, projected_gradient_residual,
)
from scratch_transplant_opt import information_metrics, reflected_law


def replay_basin(obj):
    initial = reflected_law()
    uniform = np.full(initial.shape, 1.0 / initial.size)
    rng = np.random.default_rng(2029080600)
    theta = np.log(0.99 * initial + 0.01 * uniform) + rng.normal(0.0, 1.07,
                                                               size=initial.shape)
    return obj.optimize(theta, 30000, 0.06)[1]


def align(source, target):
    best = (-1.0, None)
    perms = list(itertools.permutations(range(4)))
    for pw in perms:
        a = source[np.asarray(pw)]
        for pu in perms:
            b = a[:, np.asarray(pu)]
            for pv in perms:
                c = b[:, :, np.asarray(pv)]
                score = float(np.sum(np.sqrt(c * target)))
                if score > best[0]:
                    best = score, c.copy()
    return best


def direct_endpoints(p, obj):
    wy = np.einsum("wuvx,xy->wy", p, obj.base_ty)
    wz = np.einsum("wuvx,xz->wz", p, obj.base_tz)
    wuy = np.einsum("wuvx,xy->wuy", p, obj.base_ty)
    wvz = np.einsum("wuvx,xz->wvz", p, obj.base_tz)
    wuv = np.sum(p, axis=3)
    y, z = np.sum(wy, axis=0), np.sum(wz, axis=0)
    common = -entropy(wuy) - entropy(wvz) + entropy(wuv)
    return entropy(y) + entropy(wz) + common, entropy(z) + entropy(wy) + common


def objective_audit(obj, p):
    simplified = obj.value_grad(p)[0]
    ey, ez = direct_endpoints(p, obj)
    direct = 0.5 * (ey + ez)
    residual = abs(simplified - direct)
    if residual > 2e-12:
        raise AssertionError((simplified, direct, residual))
    return simplified, ey, ez, residual


def optimize_from(obj, p, iterations, lr):
    uniform = np.full(p.shape, 1.0 / p.size)
    p = (1.0 - 1e-11) * p + 1e-11 * uniform
    return obj.optimize(np.log(p), iterations, lr)[1]


def orthogonal_logit_start(base, product, rng, sigma):
    floor = 1e-15
    theta = np.log(base + floor)
    chord = np.log(product + floor) - np.log(base + floor)
    chord -= np.mean(chord)
    perturbation = rng.normal(size=base.shape)
    perturbation -= np.mean(perturbation)
    perturbation -= chord * (float(np.sum(perturbation * chord))
                             / float(np.sum(chord * chord)))
    perturbation /= math.sqrt(float(np.mean(perturbation * perturbation)))
    candidate = np.exp(np.maximum(theta + sigma * perturbation
                                  - float(np.max(theta + sigma * perturbation)), -745.0))
    candidate /= np.sum(candidate)
    return candidate


def map_mutation(base, rng, amount):
    mutated = np.empty_like(base)
    for w in range(4):
        for u in range(4):
            for v in range(4):
                mutated[w, u, v] = base[w, u, v, rng.permutation(4)]
    return (1.0 - amount) * base + amount * mutated


def lift_w8(base, rng, amount):
    out = np.zeros((8, 4, 4, 4))
    for w in range(4):
        out[w] = 0.5 * base[w]
        mutation = np.empty_like(base[w])
        for u in range(4):
            for v in range(4):
                mutation[u, v] = base[w, u, v, rng.permutation(4)]
        out[4 + w] = 0.5 * ((1.0 - amount) * base[w] + amount * mutation)
    out /= np.sum(out)
    return out


def report(family, weight, seed, p, obj, product_reference):
    value, ey, ez, audit_residual = objective_audit(obj, p)
    px = np.sum(p, axis=(0, 1, 2))
    print("ESCAPE", family, "weight", weight, "seed", seed,
          "bits", repr(value / LN2),
          "margin_bits", repr((value - TARGET_NATS) / LN2),
          "endpoints_bits", (ey / LN2, ez / LN2),
          "objective_audit_residual_nats", audit_residual,
          "input", px.tolist(), "min_input_mass", float(np.min(px)),
          "TV_to_product", (0.5 * float(np.sum(np.abs(p - product_reference)))
                            if p.shape == product_reference.shape else None),
          "stationarity", projected_gradient_residual(obj, p),
          "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=18000)
    parser.add_argument("--orthogonal", type=int, default=6)
    parser.add_argument("--w8", type=int, default=3)
    parser.add_argument("--weights", default="0.25,0.30,0.35,0.40,0.45,0.50")
    args = parser.parse_args()

    # Attach channel matrices as named attributes for the independent evaluator.
    from scratch_stochastic_marton import TY, TZ
    obj4 = MartonHalf()
    obj4.base_ty, obj4.base_tz = TY, TZ
    product = obj4.product_rtd()
    basin = align(replay_basin(obj4), product)[1]
    obj8 = MartonHalf(nw=8)
    obj8.base_ty, obj8.base_tz = TY, TZ
    product8 = np.zeros(obj8.shape)
    product8[:4] = product

    global_best = (-math.inf, None)
    for wi, weight in enumerate(float(x) for x in args.weights.split(",")):
        chord = (1.0 - weight) * basin + weight * product
        base = optimize_from(obj4, chord, args.iterations, 0.05)
        value = report("base", weight, 0, base, obj4, product)
        if value > global_best[0]:
            global_best = value, ("base", weight, 0)

        for j in range(args.orthogonal):
            seed = 2026082801 + 100003 * wi + 1009 * j
            rng = np.random.default_rng(seed)
            sigma = (0.15, 0.3, 0.6, 1.0, 1.5, 2.0)[j % 6]
            start = orthogonal_logit_start(base, product, rng, sigma)
            p = optimize_from(obj4, start, args.iterations, 0.055)
            value = report(f"orthogonal_sigma_{sigma}", weight, seed, p, obj4, product)
            if value > global_best[0]:
                global_best = value, ("orthogonal", weight, seed, sigma)

        for j, amount in enumerate((0.1, 0.3, 0.6)):
            seed = 2026082901 + 100003 * wi + 1009 * j
            rng = np.random.default_rng(seed)
            p = optimize_from(obj4, map_mutation(base, rng, amount),
                              args.iterations, 0.055)
            value = report(f"map_mutation_{amount}", weight, seed, p, obj4, product)
            if value > global_best[0]:
                global_best = value, ("map", weight, seed, amount)

        for j in range(args.w8):
            seed = 2026083001 + 100003 * wi + 1009 * j
            rng = np.random.default_rng(seed)
            amount = (0.15, 0.4, 0.75)[j % 3]
            p = optimize_from(obj8, lift_w8(base, rng, amount),
                              args.iterations + 6000, 0.05)
            value = report(f"W8_map_mutation_{amount}", weight, seed, p, obj8, product8)
            if value > global_best[0]:
                global_best = value, ("W8", weight, seed, amount)
    print("FINAL best_bits", global_best[0] / LN2,
          "margin_bits", (global_best[0] - TARGET_NATS) / LN2,
          "source", global_best[1], flush=True)


if __name__ == "__main__":
    main()
