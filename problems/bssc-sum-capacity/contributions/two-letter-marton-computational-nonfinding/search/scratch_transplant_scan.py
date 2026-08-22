#!/usr/bin/env python3
"""Exhaustive BSSC relabeling scan of the 2026 ternary Marton architecture.

This reads (but does not execute) the exact rational 2x4x4x9 component laws
published by Huang--Liu--Liu.  For each of the 4^9 maps from their nine
two-letter input labels to the four BSSC super-inputs, it recomputes the two
Marton endpoints and L_{1/2}.  Floating-point output is a numerical lead only.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


SOURCE = Path("/tmp/Suboptimality_Marton-audit-jdichc/data/certificates/"
              "fixed_input/cc_certificate_e5e-7.json")
SOURCE_SHA256 = "45502b2e7a694ae2d1beaee3e19249d63d9efe39b6405daa42ada0e1cbb846d6"
LN2 = math.log(2.0)
TARGET_BITS = 2.0 * 0.361642884421954615663441578150587


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


def entropy_batch(a):
    terms = np.zeros_like(a)
    positive = a > 0.0
    terms[positive] = -a[positive] * np.log(a[positive])
    return np.sum(terms.reshape(len(a), -1), axis=1)


def entropy(a):
    p = a[a > 0.0]
    return -float(p @ np.log(p))


class Component:
    def __init__(self, record):
        if record["shape"] != [2, 4, 4, 9]:
            raise ValueError(record["shape"])
        denominator = int(record["probability_denominator"])
        self.p = (np.asarray(record["probability_numerators"], dtype=np.float64)
                  .reshape(2, 4, 4, 9) / denominator)
        if abs(float(np.sum(self.p)) - 1.0) > 2e-15:
            raise AssertionError("source simplex residual")
        self.row = int(record["row_index"])
        self.wx = np.sum(self.p, axis=(1, 2))
        self.wux = np.sum(self.p, axis=2)
        self.wvx = np.sum(self.p, axis=1)
        self.x = np.sum(self.p, axis=(0, 1, 2))
        self.h_wuv = entropy(np.sum(self.p, axis=3))

    def evaluate(self, maps):
        ky = TY[maps]
        kz = TZ[maps]
        y = np.einsum("i,biy->by", self.x, ky)
        z = np.einsum("i,biz->bz", self.x, kz)
        wy = np.einsum("wi,biy->bwy", self.wx, ky)
        wz = np.einsum("wi,biz->bwz", self.wx, kz)
        wuy = np.einsum("wui,biy->bwuy", self.wux, ky)
        wvz = np.einsum("wvi,biz->bwvz", self.wvx, kz)
        common = -entropy_batch(wuy) - entropy_batch(wvz) + self.h_wuv
        endpoint_y = entropy_batch(y) + entropy_batch(wz) + common
        endpoint_z = entropy_batch(z) + entropy_batch(wy) + common
        return endpoint_y, endpoint_z

    def mapped_input(self, mapping):
        return np.bincount(mapping, weights=self.x, minlength=4)


def digits_base4(start, stop):
    ids = np.arange(start, stop, dtype=np.uint32)
    return np.stack([(ids // (4 ** j)) % 4 for j in range(9)], axis=1)


def separable_orientations(mapping):
    a = np.asarray(mapping).reshape(3, 3)
    first = a // 2
    second = a % 2
    normal = (all(np.all(first[r] == first[r, 0]) for r in range(3))
              and all(np.all(second[:, c] == second[0, c])
                      for c in range(3)))
    swapped = (all(np.all(first[:, c] == first[0, c]) for c in range(3))
               and all(np.all(second[r] == second[r, 0])
                       for r in range(3)))
    return normal, swapped


def rectangular(mapping):
    return any(separable_orientations(mapping))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=4096)
    parser.add_argument("--top", type=int, default=16)
    args = parser.parse_args()

    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise AssertionError((digest, SOURCE_SHA256))
    data = json.loads(SOURCE.read_text())
    records = data["winning_schemes"]
    if len(records) != 2:
        raise AssertionError(len(records))
    components = [Component(record) for record in records]

    total = 4 ** 9
    top = [[] for _ in components]
    support_max = [[-math.inf] * 5 for _ in components]
    separable_max = [[-math.inf, -math.inf] for _ in components]
    for start in range(0, total, args.batch):
        stop = min(total, start + args.batch)
        maps = digits_base4(start, stop)
        for ci, component in enumerate(components):
            ey, ez = component.evaluate(maps)
            half = 0.5 * (ey + ez) / LN2
            local_count = min(args.top, len(half))
            local = np.argpartition(half, -local_count)[-local_count:]
            for j in local:
                mapping = tuple(int(x) for x in maps[j])
                item = (float(half[j]), float(ey[j] / LN2),
                        float(ez[j] / LN2), start + int(j), mapping)
                top[ci].append(item)
            top[ci] = sorted(top[ci], reverse=True)[:args.top]

            for j, mapping in enumerate(maps):
                size = len(set(int(x) for x in mapping))
                if half[j] > support_max[ci][size]:
                    support_max[ci][size] = float(half[j])
                normal, swapped = separable_orientations(mapping)
                if normal and half[j] > separable_max[ci][0]:
                    separable_max[ci][0] = float(half[j])
                if swapped and half[j] > separable_max[ci][1]:
                    separable_max[ci][1] = float(half[j])
        if start % (32 * args.batch) == 0:
            print("checkpoint", stop, "/", total,
                  [(c.row, top[i][0][0]) for i, c in enumerate(components)],
                  flush=True)

    print("source", str(SOURCE), "sha256", digest)
    print("coverage", total, "maps per component", len(components), "components")
    for ci, component in enumerate(components):
        print("COMPONENT", component.row,
              "support_max_bits", support_max[ci][1:],
              "normal_separable_max_bits", separable_max[ci][0],
              "swapped_separable_max_bits", separable_max[ci][1],
              "either_separable_max_bits", max(separable_max[ci]))
        for rank, item in enumerate(top[ci]):
            half, ey, ez, map_id, mapping = item
            px = component.mapped_input(mapping)
            print("TOP", rank, "map_id", map_id, "map", mapping,
                  "Lhalf_bits", repr(half), "margin_bits", repr(half - TARGET_BITS),
                  "Y_bits", repr(ey), "Z_bits", repr(ez),
                  "input", px.tolist(),
                  "separable_orientations", separable_orientations(mapping))


if __name__ == "__main__":
    main()
