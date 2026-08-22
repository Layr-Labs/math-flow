#!/usr/bin/env python3
"""Fixed-input full-joint L_1/2 search on the symmetry-reduced BSSC line."""

import argparse
import math
import numpy as np

from scratch_stochastic_marton import LN2, MartonHalf, TARGET_NATS
from scratch_transplant_opt import reflected_law


def conditional_softmax(theta, px):
    flat = theta.reshape(-1, 4)
    shifted = flat - np.max(flat, axis=0, keepdims=True)
    q = np.exp(np.maximum(shifted, -745.0))
    q /= np.sum(q, axis=0, keepdims=True)
    return (q * px[None, :]).reshape(theta.shape)


class FixedInput:
    def __init__(self, nw=4, nu=4, nv=4):
        self.base = MartonHalf(nw=nw, nu=nu, nv=nv)
        self.shape = self.base.shape

    def optimize(self, theta, px, iterations=20000, lr=0.07):
        m = np.zeros(self.shape)
        v = np.zeros(self.shape)
        best = (-math.inf, None, None)
        for it in range(1, iterations + 1):
            p = conditional_softmax(theta, px)
            value, gp = self.base.value_grad(p)
            if value > best[0]:
                best = value, p.copy(), it
            q = p / px[None, None, None, :]
            mean = np.sum(q * gp, axis=(0, 1, 2), keepdims=True)
            gt = p * (gp - mean)
            m = 0.9 * m + 0.1 * gt
            v = 0.999 * v + 0.001 * gt * gt
            mh = m / (1.0 - 0.9 ** it)
            vh = v / (1.0 - 0.999 ** it)
            frac = (it - 1.0) / max(1.0, iterations - 1.0)
            step = lr * (0.06 + 0.94 * (1.0 - frac) ** 2)
            theta += step * mh / (np.sqrt(vh) + 1e-14)
            theta -= np.max(theta, axis=(0, 1, 2), keepdims=True)
            np.maximum(theta, -90.0, out=theta)
        return best

    def gradient_check(self, px, seed=2026082601):
        rng = np.random.default_rng(seed)
        theta = rng.normal(0.0, 0.5, size=self.shape)
        p = conditional_softmax(theta, px)
        value, gp = self.base.value_grad(p)
        q = p / px[None, None, None, :]
        mean = np.sum(q * gp, axis=(0, 1, 2), keepdims=True)
        gt = p * (gp - mean)
        d = rng.normal(size=self.shape)
        d -= np.mean(d, axis=(0, 1, 2), keepdims=True)
        d /= np.max(np.abs(d))
        h = 1e-6
        fd = (self.base.value_grad(conditional_softmax(theta + h * d, px))[0]
              - self.base.value_grad(conditional_softmax(theta - h * d, px))[0]) / (2*h)
        analytic = float(np.sum(gt * d))
        return value, fd, analytic, abs(fd - analytic)


def conditional_logits(law, px, floor=1e-12):
    q = law / np.sum(law, axis=(0, 1, 2), keepdims=True)
    q = (1.0 - floor) * q + floor / np.prod(q.shape[:3])
    return np.log(q)


def fixed_stationarity(obj, p):
    _, g = obj.base.value_grad(p)
    out = []
    for x in range(4):
        q = p[..., x] / np.sum(p[..., x])
        active = q > 1e-9
        lam = float(np.sum(q[active] * g[..., x][active]) / np.sum(q[active]))
        spread = float(np.max(np.abs(g[..., x][active] - lam)))
        excess = (float(np.max(g[..., x][~active] - lam))
                  if np.any(~active) else 0.0)
        out.append((spread, max(0.0, excess), int(np.sum(active))))
    return out


def replay_reflected_optimum(base):
    initial = reflected_law()
    uniform = np.full(initial.shape, 1.0 / initial.size)
    rng = np.random.default_rng(2029080600)
    theta = np.log(0.99 * initial + 0.01 * uniform) + rng.normal(0.0, 1.07,
                                                               size=initial.shape)
    return base.optimize(theta, 30000, 0.06)[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20000)
    parser.add_argument("--random-starts", type=int, default=4)
    parser.add_argument("--grid", default="0.02,0.05,0.10,0.15,0.20,0.23,0.24,0.25,0.26,0.27,0.30,0.35,0.40,0.45,0.48")
    args = parser.parse_args()

    obj = FixedInput()
    product = obj.base.product_rtd()
    reflected = replay_reflected_optimum(obj.base)
    check = obj.gradient_check(np.full(4, 0.25))
    print("gradient_check", check, flush=True)
    if check[-1] > 2e-7 * max(1.0, abs(check[1]), abs(check[2])):
        raise AssertionError(check)

    global_best = (-math.inf, None)
    for ai, a in enumerate(float(x) for x in args.grid.split(",")):
        px = np.asarray((a, 0.5 - a, 0.5 - a, a))
        starts = [("product_conditional", conditional_logits(product, px)),
                  ("reflected_conditional", conditional_logits(reflected, px))]
        for j in range(args.random_starts):
            seed = 2026082701 + 100003 * ai + 1009 * j
            rng = np.random.default_rng(seed)
            starts.append((f"random_{seed}", rng.normal(0.0, 1.8, size=obj.shape)))
        best = (-math.inf, None)
        for label, theta in starts:
            value, p, best_it = obj.optimize(theta.copy(), px, args.iterations)
            if value > best[0]:
                best = value, (label, p, best_it)
            print("FIXED", "a", a, "start", label,
                  "bits", repr(value / LN2),
                  "margin_bits", repr((value - TARGET_NATS) / LN2),
                  "best_it", best_it,
                  "input_residual", float(np.max(np.abs(np.sum(p, axis=(0,1,2)) - px))),
                  "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)
        value, (label, p, best_it) = best
        stationarity = fixed_stationarity(obj, p)
        print("FIXED_FINAL", "a", a, "best_start", label,
              "bits", repr(value / LN2),
              "margin_bits", repr((value - TARGET_NATS) / LN2),
              "stationarity_by_x", stationarity,
              "min_input_mass", float(np.min(px)), flush=True)
        if value > global_best[0]:
            global_best = value, (a, label, p, stationarity)
    value, (a, label, p, stationarity) = global_best
    print("FINAL", "a", a, "start", label, "bits", repr(value / LN2),
          "margin_bits", repr((value - TARGET_NATS) / LN2),
          "input", np.sum(p, axis=(0,1,2)).tolist(),
          "stationarity_by_x", stationarity, flush=True)


if __name__ == "__main__":
    main()
