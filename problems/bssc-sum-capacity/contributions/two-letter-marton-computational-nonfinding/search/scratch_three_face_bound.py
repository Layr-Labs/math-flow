#!/usr/bin/env python3
"""Adversarial numerical check of the proposed support-at-most-three bound.

For every three-symbol face, test

    M(P) <= 0.5[I(X^2;Y^2)+I(X^2;Z^2)] + 2 r,
    r = h2(1/4)-3/4.

This is validation-only floating-point code; it is not part of the proof.
"""

import argparse
import math
import numpy as np

from scratch_stochastic_marton import (
    LN2, MartonHalf, TY, TZ, entropy, projected_gradient_residual, softmax,
)
from scratch_transplant_opt import reflected_law, source_law


R_NATS = (-(0.25 * math.log(0.25) + 0.75 * math.log(0.75))
          - 0.75 * LN2)


class FaceViolation:
    def __init__(self, face, nw=4, nu=4, nv=4):
        self.face = tuple(face)
        self.ky = TY[np.asarray(face)]
        self.kz = TZ[np.asarray(face)]
        self.hy_row = np.asarray([entropy(row) for row in self.ky])
        self.hz_row = np.asarray([entropy(row) for row in self.kz])
        self.shape = (nw, nu, nv, len(face))

    def terms_grad(self, p):
        wy = np.einsum("wuvx,xy->wy", p, self.ky)
        wz = np.einsum("wuvx,xz->wz", p, self.kz)
        wuy = np.einsum("wuvx,xy->wuy", p, self.ky)
        wvz = np.einsum("wuvx,xz->wvz", p, self.kz)
        wuv = np.sum(p, axis=3)
        px = np.sum(p, axis=(0, 1, 2))
        y = np.sum(wy, axis=0)
        z = np.sum(wz, axis=0)

        common = -entropy(wuy) - entropy(wvz) + entropy(wuv)
        endpoint_y = entropy(y) + entropy(wz) + common
        endpoint_z = entropy(z) + entropy(wy) + common
        marton = min(endpoint_y, endpoint_z)
        g_input = (0.5 * (entropy(y) + entropy(z))
                   - 0.5 * float(px @ (self.hy_row + self.hz_row)))
        rhs = g_input + 2.0 * R_NATS
        violation = marton - rhs

        tiny = np.finfo(np.float64).tiny
        lp = lambda a: np.log(np.maximum(a, tiny)) + 1.0
        ly, lz = lp(y), lp(z)
        lwy, lwz = lp(wy), lp(wz)
        lwuy, lwvz, lwuv = lp(wuy), lp(wvz), lp(wuv)
        private = (np.einsum("xy,wuy->wux", self.ky, lwuy)[:, :, None, :]
                   + np.einsum("xz,wvz->wvx", self.kz, lwvz)[:, None, :, :]
                   - lwuv[:, :, :, None])
        gy = (-self.ky @ ly)[None, None, None, :] \
            - np.einsum("xz,wz->wx", self.kz, lwz)[:, None, None, :] + private
        gz = (-self.kz @ lz)[None, None, None, :] \
            - np.einsum("xy,wy->wx", self.ky, lwy)[:, None, None, :] + private
        if endpoint_y < endpoint_z - 1e-10:
            gm = gy
        elif endpoint_z < endpoint_y - 1e-10:
            gm = gz
        else:
            gm = 0.5 * (gy + gz)
        ggx = (-0.5 * (self.ky @ ly + self.kz @ lz)
               - 0.5 * (self.hy_row + self.hz_row))
        gv = gm - ggx[None, None, None, :]
        return violation, gv, endpoint_y, endpoint_z, g_input, rhs

    def optimize(self, theta, iterations=15000, lr=0.07):
        m = np.zeros(self.shape)
        v = np.zeros(self.shape)
        best = (-math.inf, None, None)
        for it in range(1, iterations + 1):
            p = softmax(theta)
            value, gp, ey, ez, g, rhs = self.terms_grad(p)
            if value > best[0]:
                best = value, p.copy(), (ey, ez, g, rhs, it)
            gt = p * (gp - float(np.sum(p * gp)))
            m = 0.9 * m + 0.1 * gt
            v = 0.999 * v + 0.001 * gt * gt
            mh = m / (1.0 - 0.9 ** it)
            vh = v / (1.0 - 0.999 ** it)
            frac = (it - 1.0) / max(1.0, iterations - 1.0)
            step = lr * (0.08 + 0.92 * (1.0 - frac) ** 2)
            theta += step * mh / (np.sqrt(vh) + 1e-14)
            theta -= float(np.max(theta))
            np.maximum(theta, -90.0, out=theta)
        return best

    def finite_difference(self, seed):
        rng = np.random.default_rng(seed)
        p = rng.random(self.shape)
        p /= np.sum(p)
        d = rng.normal(size=self.shape)
        d -= np.mean(d)
        d /= np.max(np.abs(d))
        # Break the endpoint tie so the active branch is differentiable.
        p *= rng.lognormal(0.0, 0.2, size=self.shape)
        p /= np.sum(p)
        value, grad, ey, ez, _, _ = self.terms_grad(p)
        h = 0.01 * float(np.min(p))
        fd = (self.terms_grad(p + h * d)[0]
              - self.terms_grad(p - h * d)[0]) / (2.0 * h)
        analytic = float(np.sum(grad * d))
        return value, ey - ez, fd, analytic, abs(fd - analytic)


def projected_candidate(name, full_p, face):
    p = full_p[..., list(face)].copy()
    p /= np.sum(p)
    obj = FaceViolation(face, nw=p.shape[0])
    value, _, ey, ez, g, rhs = obj.terms_grad(p)
    return name, value / LN2, ey / LN2, ez / LN2, g / LN2, rhs / LN2


def replay_reflected_optimum():
    obj = MartonHalf()
    initial = reflected_law()
    uniform = np.full(initial.shape, 1.0 / initial.size)
    rng = np.random.default_rng(2029080600)
    p0 = 0.99 * initial + 0.01 * uniform
    theta = np.log(p0) + rng.normal(0.0, 1.07, size=initial.shape)
    return obj.optimize(theta, 30000, 0.06)[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", type=int, default=5000)
    parser.add_argument("--starts", type=int, default=12)
    parser.add_argument("--iterations", type=int, default=15000)
    args = parser.parse_args()

    product = MartonHalf().product_rtd()
    reflected = reflected_law()
    raw = source_law()
    reflected_opt = replay_reflected_optimum()
    global_best = (-math.inf, None)
    for excluded in range(4):
        face = tuple(x for x in range(4) if x != excluded)
        obj = FaceViolation(face)
        check = obj.finite_difference(2026082301 + excluded)
        print("FACE", face, "gradient_check", check, flush=True)
        if check[-1] > 2e-6 * max(1.0, abs(check[2]), abs(check[3])):
            raise AssertionError((face, check))

        random_best = (-math.inf, None)
        rng = np.random.default_rng(2026082401 + 1009 * excluded)
        for j in range(args.random):
            alpha = 10.0 ** rng.uniform(-1.7, 0.7)
            p = rng.gamma(alpha, 1.0, size=obj.shape)
            p /= np.sum(p)
            value, _, ey, ez, g, rhs = obj.terms_grad(p)
            if value > random_best[0]:
                random_best = value, (j, alpha, ey, ez, g, rhs)
        print("RANDOM_BEST", face, "draws", args.random,
              "violation_bits", random_best[0] / LN2,
              "details", random_best[1], flush=True)

        opt_best = (-math.inf, None)
        for j in range(args.starts):
            seed = 2026082501 + 100003 * excluded + 1009 * j
            rng = np.random.default_rng(seed)
            theta = rng.normal(0.0, 1.8, size=obj.shape)
            value, p, details = obj.optimize(theta, args.iterations)
            if value > opt_best[0]:
                opt_best = value, (seed, p, details)
            print("OPT", face, j, "seed", seed,
                  "violation_bits", value / LN2,
                  "endpoints_bits", (details[0] / LN2, details[1] / LN2),
                  "G_bits", details[2] / LN2, "rhs_bits", details[3] / LN2,
                  "best_it", details[4],
                  "input", np.sum(p, axis=(0, 1, 2)).tolist(),
                  "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)

        for candidate in (projected_candidate("product", product, face),
                          projected_candidate("raw_transplant", raw, face),
                          projected_candidate("reflected_transplant", reflected, face),
                          projected_candidate("reflected_optimized", reflected_opt, face)):
            print("PROJECTED", face, candidate, flush=True)
            if candidate[1] > global_best[0]:
                global_best = candidate[1], ("projected", face, candidate)
        if random_best[0] / LN2 > global_best[0]:
            global_best = random_best[0] / LN2, ("random", face, random_best[1])
        if opt_best[0] / LN2 > global_best[0]:
            global_best = opt_best[0] / LN2, ("optimized", face, opt_best[1][0], opt_best[1][2])
        print("FACE_FINAL", face,
              "optimized_max_violation_bits", opt_best[0] / LN2,
              "random_max_violation_bits", random_best[0] / LN2, flush=True)
    print("FINAL maximum_violation_bits", global_best[0], "witness", global_best[1],
          "constant_2r_bits", 2.0 * R_NATS / LN2, flush=True)


if __name__ == "__main__":
    main()
