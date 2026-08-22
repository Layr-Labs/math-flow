#!/usr/bin/env python3
"""Full-joint floating-point search for two-letter half-skew BSSC Marton gain.

Discovery code only: this optimizes p(w,u,v,x1x2), including stochastic
X|(W,U,V), for the smooth half-weight Marton functional.  It deliberately
uses only NumPy and fixed seeds.  Floating-point output is not a proof.
"""

import argparse
import math
import numpy as np


LN2 = math.log(2.0)
ONE_RTD_BITS = 0.361642884421954615663441578150587
TARGET_NATS = 2.0 * ONE_RTD_BITS * LN2
A_RTD = 0.1584349792600164


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


def entropy(a):
    positive = a[a > 0.0]
    return -float(positive @ np.log(positive))


def softmax(theta):
    shifted = theta.ravel() - float(np.max(theta))
    ex = np.exp(np.maximum(shifted, -745.0))
    return (ex / float(np.sum(ex))).reshape(theta.shape)


class MartonHalf:
    def __init__(self, nw=4, nu=4, nv=4):
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

        value = (0.5 * entropy(y) + 0.5 * entropy(z)
                 + 0.5 * entropy(wy) + 0.5 * entropy(wz)
                 - entropy(wuy) - entropy(wvz) + entropy(wuv))

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
        grad = (gx[None, None, None, :]
                + gwy[:, None, None, :] + gwz[:, None, None, :]
                + gwuy[:, :, None, :] + gwvz[:, None, :, :]
                - lwuv[:, :, :, None])
        return value, grad

    def product_rtd(self):
        if self.nw < 4 or self.nu < 4 or self.nv < 4:
            raise ValueError("product RTD seed needs W,U,V cardinality at least 4")
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
                        u = 2 * (x1 if w1 == 0 else 0) + (x2 if w2 == 0 else 0)
                        v = 2 * (x1 if w1 == 1 else 0) + (x2 if w2 == 1 else 0)
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
        h = 0.01 * float(np.min(p))
        value, grad = self.value_grad(p)
        fd = (self.value_grad(p + h * direction)[0]
              - self.value_grad(p - h * direction)[0]) / (2.0 * h)
        analytic = float(np.sum(grad * direction))
        return value, fd, analytic, abs(fd - analytic)

    def optimize(self, theta, iterations, lr):
        m = np.zeros(self.shape, dtype=np.float64)
        v = np.zeros(self.shape, dtype=np.float64)
        best_value = -math.inf
        best_p = None
        best_it = 0
        for it in range(1, iterations + 1):
            p = softmax(theta)
            value, gp = self.value_grad(p)
            if value > best_value:
                best_value, best_p, best_it = value, p.copy(), it
            centered = gp - float(np.sum(p * gp))
            gt = p * centered
            m = 0.9 * m + 0.1 * gt
            v = 0.999 * v + 0.001 * gt * gt
            mh = m / (1.0 - 0.9 ** it)
            vh = v / (1.0 - 0.999 ** it)
            frac = (it - 1.0) / max(1.0, iterations - 1.0)
            step = lr * (0.05 + 0.95 * (1.0 - frac) ** 2)
            theta += step * mh / (np.sqrt(vh) + 1e-14)
            theta -= float(np.max(theta))
            np.maximum(theta, -90.0, out=theta)
        return best_value, best_p, best_it


def projected_gradient_residual(obj, p):
    _, g = obj.value_grad(p)
    active = p > 1e-10
    lam = float(np.sum(p[active] * g[active]) / np.sum(p[active]))
    active_spread = float(np.max(np.abs(g[active] - lam)))
    inactive_violation = float(np.max(g[~active] - lam)) if np.any(~active) else 0.0
    return active_spread, max(0.0, inactive_violation), int(np.sum(active))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=24)
    parser.add_argument("--iterations", type=int, default=12000)
    parser.add_argument("--nw", type=int, default=4)
    parser.add_argument("--nu", type=int, default=4)
    parser.add_argument("--nv", type=int, default=4)
    parser.add_argument("--lr", type=float, default=0.08)
    args = parser.parse_args()

    obj = MartonHalf(nw=args.nw, nu=args.nu, nv=args.nv)
    print("shape", obj.shape, "target_bits", TARGET_NATS / LN2, flush=True)
    fd = obj.finite_difference()
    print("finite_difference", fd, flush=True)
    need_fd = 5e-6 * max(1.0, abs(fd[1]), abs(fd[2]))
    if fd[3] > need_fd:
        raise AssertionError(("gradient check failed", fd, need_fd))

    product = obj.product_rtd()
    product_value = obj.value_grad(product)[0]
    print("product_seed_bits", product_value / LN2,
          "target_residual_bits", (product_value - TARGET_NATS) / LN2,
          "simplex_residual", abs(float(np.sum(product)) - 1.0), flush=True)

    best = (-math.inf, None, None, None)
    uniform = np.full(obj.shape, 1.0 / np.prod(obj.shape))
    for seed_index in range(args.seeds):
        seed = 2026082201 + 104729 * seed_index
        rng = np.random.default_rng(seed)
        if seed_index < args.seeds // 2:
            epsilon = 10.0 ** (-8.0 + 6.0 * seed_index / max(1, args.seeds // 2 - 1))
            p0 = (1.0 - epsilon) * product + epsilon * uniform
            theta = np.log(p0) + rng.normal(0.0, 0.35 + 0.12 * seed_index,
                                             size=obj.shape)
            family = "product"
        else:
            theta = rng.normal(0.0, 1.5, size=obj.shape)
            family = "interior"
        value, p, best_it = obj.optimize(theta, args.iterations, args.lr)
        active_spread, inactive_violation, support = projected_gradient_residual(obj, p)
        bits = value / LN2
        print("run", seed_index, "seed", seed, "family", family,
              "bits", repr(bits), "margin_bits", repr(bits - TARGET_NATS / LN2),
              "best_it", best_it, "support", support,
              "active_grad_spread", active_spread,
              "inactive_grad_violation", inactive_violation,
              "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)
        if value > best[0]:
            best = (value, p, seed, family)

    value, p, seed, family = best
    active_spread, inactive_violation, support = projected_gradient_residual(obj, p)
    px = np.sum(p, axis=(0, 1, 2))
    print("FINAL seed", seed, "family", family,
          "bits", repr(value / LN2),
          "margin_bits", repr((value - TARGET_NATS) / LN2),
          "input", px.tolist(), "support", support,
          "active_grad_spread", active_spread,
          "inactive_grad_violation", inactive_violation,
          "simplex_residual", abs(float(np.sum(p)) - 1.0), flush=True)


if __name__ == "__main__":
    main()
