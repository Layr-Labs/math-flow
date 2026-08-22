#!/usr/bin/env python3
"""Independent exact-rational/100-digit audit of transplanted Marton laws."""

import hashlib
import json
from decimal import Context, Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path

SOURCE = Path("/tmp/Suboptimality_Marton-audit-jdichc/data/certificates/"
              "fixed_input/cc_certificate_e5e-7.json")
SOURCE_SHA256 = "45502b2e7a694ae2d1beaee3e19249d63d9efe39b6405daa42ada0e1cbb846d6"
MAPPING = (1, 0, 3, 0, 0, 2, 3, 2, 3)
getcontext().prec = 100
CTX = Context(prec=100)
D = Decimal
LN2 = CTX.ln(D(2))


def product_channel(base):
    return [[base[x // 2][y // 2] * base[x % 2][y % 2]
             for y in range(4)] for x in range(4)]


TY = product_channel([[F(1, 2), F(1, 2)], [F(0), F(1)]])
TZ = product_channel([[F(1), F(0)], [F(1, 2), F(1, 2)]])


def h(values):
    out = D(0)
    for probability in values:
        if probability:
            p = CTX.divide(D(probability.numerator), D(probability.denominator))
            out = CTX.subtract(out, CTX.divide(CTX.multiply(p, CTX.ln(p)), LN2))
    return out


def marginal(p, keep):
    sizes = (len(p), len(p[0]), len(p[0][0]), len(p[0][0][0]))
    out = {}
    for w in range(sizes[0]):
        for u in range(sizes[1]):
            for v in range(sizes[2]):
                for x in range(sizes[3]):
                    key_all = (w, u, v, x)
                    key = tuple(key_all[i] for i in keep)
                    out[key] = out.get(key, F(0)) + p[w][u][v][x]
    return list(out.values())


def output_marginal(p, receiver, keep):
    # keep is a subset of W,U,V; append the receiver output.
    sizes = (len(p), len(p[0]), len(p[0][0]), len(p[0][0][0]))
    out = {}
    for w in range(sizes[0]):
        for u in range(sizes[1]):
            for v in range(sizes[2]):
                for x in range(sizes[3]):
                    mass = p[w][u][v][x]
                    for y, transition in enumerate(receiver[x]):
                        key_all = (w, u, v)
                        key = tuple(key_all[i] for i in keep) + (y,)
                        out[key] = out.get(key, F(0)) + mass * transition
    return list(out.values())


def split_entropy(p, fields, receiver=None):
    """Entropy of named split-coordinate fields, retaining exact masses."""
    sizes = (len(p), len(p[0]), len(p[0][0]), len(p[0][0][0]))
    out = {}
    for w in range(sizes[0]):
        for u in range(sizes[1]):
            u1, u2 = divmod(u, 2)
            for v in range(sizes[2]):
                v1, v2 = divmod(v, 2)
                for x in range(sizes[3]):
                    x1, x2 = divmod(x, 2)
                    mass = p[w][u][v][x]
                    outputs = [(None, F(1))] if receiver is None else enumerate(receiver[x])
                    for output, transition in outputs:
                        values = {"w": w, "u": u, "v": v,
                                  "u1": u1, "u2": u2,
                                  "v1": v1, "v2": v2,
                                  "x1": x1, "x2": x2}
                        if receiver is not None:
                            values["o1"], values["o2"] = divmod(output, 2)
                        key = tuple(values[field] for field in fields)
                        out[key] = out.get(key, F(0)) + mass * transition
    return h(out.values())


def conditional_entropy(p, targets, conditions=(), receiver=None):
    return (split_entropy(p, tuple(conditions) + tuple(targets), receiver)
            - split_entropy(p, tuple(conditions), receiver))


def coordinate_lhalf(p, coordinate):
    y = ((F(1, 2), F(1, 2)), (F(0), F(1)))
    z = ((F(1), F(0)), (F(1, 2), F(1, 2)))
    tables = {name: {} for name in ("y", "z", "wy", "wz", "wuy", "wvz", "wuv")}

    def add(table, key, value):
        tables[table][key] = tables[table].get(key, F(0)) + value

    for w in range(len(p)):
        for u in range(4):
            ub = divmod(u, 2)[coordinate]
            for v in range(4):
                vb = divmod(v, 2)[coordinate]
                for x in range(4):
                    xb = divmod(x, 2)[coordinate]
                    mass = p[w][u][v][x]
                    add("wuv", (w, ub, vb), mass)
                    for output, transition in enumerate(y[xb]):
                        add("y", (output,), mass * transition)
                        add("wy", (w, output), mass * transition)
                        add("wuy", (w, ub, output), mass * transition)
                    for output, transition in enumerate(z[xb]):
                        add("z", (output,), mass * transition)
                        add("wz", (w, output), mass * transition)
                        add("wvz", (w, vb, output), mass * transition)
    return (h(tables["y"].values()) + h(tables["z"].values())
            + h(tables["wy"].values()) + h(tables["wz"].values())) / 2 \
        - h(tables["wuy"].values()) - h(tables["wvz"].values()) \
        + h(tables["wuv"].values())


def correlation_ledger(name, p, twoletter_lhalf):
    tc_u_w = (conditional_entropy(p, ("u1",), ("w",))
              + conditional_entropy(p, ("u2",), ("w",))
              - conditional_entropy(p, ("u1", "u2"), ("w",)))
    g_uy = (conditional_entropy(p, ("o1",), ("u1", "w"), TY)
            + conditional_entropy(p, ("o2",), ("u2", "w"), TY)
            - conditional_entropy(p, ("o1", "o2"), ("u1", "u2", "w"), TY))
    g_vz = (conditional_entropy(p, ("o1",), ("v1", "w"), TZ)
            + conditional_entropy(p, ("o2",), ("v2", "w"), TZ)
            - conditional_entropy(p, ("o1", "o2"), ("v1", "v2", "w"), TZ))
    g_uv = (conditional_entropy(p, ("u1",), ("v1", "w"))
            + conditional_entropy(p, ("u2",), ("v2", "w"))
            - conditional_entropy(p, ("u1", "u2"), ("v1", "v2", "w")))
    tc_y_w = (conditional_entropy(p, ("o1",), ("w",), TY)
              + conditional_entropy(p, ("o2",), ("w",), TY)
              - conditional_entropy(p, ("o1", "o2"), ("w",), TY))
    tc_z_w = (conditional_entropy(p, ("o1",), ("w",), TZ)
              + conditional_entropy(p, ("o2",), ("w",), TZ)
              - conditional_entropy(p, ("o1", "o2"), ("w",), TZ))
    tc_y = (split_entropy(p, ("o1",), TY) + split_entropy(p, ("o2",), TY)
            - split_entropy(p, ("o1", "o2"), TY))
    tc_z = (split_entropy(p, ("o1",), TZ) + split_entropy(p, ("o2",), TZ)
            - split_entropy(p, ("o1", "o2"), TZ))
    left = tc_u_w + g_uy + g_vz - g_uv
    right = (tc_y_w + tc_y + tc_z_w + tc_z) / 2
    delta = left - right
    coordinate_sum = coordinate_lhalf(p, 0) + coordinate_lhalf(p, 1)
    identity_residual = twoletter_lhalf - coordinate_sum - delta
    if abs(identity_residual) > D("1e-90"):
        raise AssertionError(("ledger identity", identity_residual))
    for key, value in (("TC(U^2|W)", tc_u_w), ("G_UY", g_uy),
                       ("G_VZ", g_vz), ("G_UV", g_uv),
                       ("TC(Y^2|W)", tc_y_w), ("TC(Y^2)", tc_y),
                       ("TC(Z^2|W)", tc_z_w), ("TC(Z^2)", tc_z),
                       ("left", left), ("right", right), ("Delta", delta),
                       ("sum_coordinate_Lhalf", coordinate_sum),
                       ("identity_residual", identity_residual)):
        print(name, "ledger", key, format(value, ".75g"))

    a1 = (conditional_entropy(p, ("o2",), ("w",), TY)
          - conditional_entropy(p, ("o2",), ("o1", "u", "w"), TY))
    a2 = (conditional_entropy(p, ("o1",), ("w",), TY)
          - conditional_entropy(p, ("o1",), ("o2", "u", "w"), TY))
    b1 = (conditional_entropy(p, ("o2",), ("w",), TZ)
          - conditional_entropy(p, ("o2",), ("o1", "v", "w"), TZ))
    b2 = (conditional_entropy(p, ("o1",), ("w",), TZ)
          - conditional_entropy(p, ("o1",), ("o2", "v", "w"), TZ))
    d_uv = (conditional_entropy(p, ("u",), ("w",))
            - conditional_entropy(p, ("u",), ("v", "w")))
    print(name, "screen", "A1", format(a1, ".75g"),
          "A2", format(a2, ".75g"), "B1", format(b1, ".75g"),
          "B2", format(b2, ".75g"), "C", format(right, ".75g"),
          "D", format(d_uv, ".75g"))
    for ai, av in enumerate((a1, a2), 1):
        for bi, bv in enumerate((b1, b2), 1):
            slack = av + bv - right - (d_uv if ai != bi else D(0))
            print(name, "screen", f"slack_{ai}{bi}", format(slack, ".75g"))
    return left, right, delta


def exact_laws():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise AssertionError((digest, SOURCE_SHA256))
    data = json.loads(SOURCE.read_text())
    record = next(r for r in data["winning_schemes"] if int(r["row_index"]) == 7)
    d = int(record["probability_denominator"])
    flat = [int(x) for x in record["probability_numerators"]]
    raw = [[[[F(0) for _ in range(4)] for _ in range(4)]
            for _ in range(4)] for _ in range(2)]
    k = 0
    for w in range(2):
        for u in range(4):
            for v in range(4):
                for old_x in range(9):
                    raw[w][u][v][MAPPING[old_x]] += F(flat[k], d)
                    k += 1
    reflected = [[[[F(0) for _ in range(4)] for _ in range(4)]
                  for _ in range(4)] for _ in range(4)]
    for w in range(2):
        for u in range(4):
            for v in range(4):
                for x in range(4):
                    reflected[w][u][v][x] += raw[w][u][v][x] / 2
                    reflected[2 + w][v][u][3 - x] += raw[w][u][v][x] / 2
    return digest, raw, reflected


def audit(name, p):
    hw = h(marginal(p, (0,)))
    hwu = h(marginal(p, (0, 1)))
    hwv = h(marginal(p, (0, 2)))
    hwuv = h(marginal(p, (0, 1, 2)))
    hy = h(output_marginal(p, TY, ()))
    hz = h(output_marginal(p, TZ, ()))
    hwy = h(output_marginal(p, TY, (0,)))
    hwz = h(output_marginal(p, TZ, (0,)))
    hwuy = h(output_marginal(p, TY, (0, 1)))
    hwvz = h(output_marginal(p, TZ, (0, 2)))

    iwy = hw + hy - hwy
    iwz = hw + hz - hwz
    iuyw = hwu + hwy - hw - hwuy
    ivzw = hwv + hwz - hw - hwvz
    iuvw = hwu + hwv - hw - hwuv
    j = iuyw + ivzw - iuvw
    endpoint_y = iwy + j
    endpoint_z = iwz + j
    half = (endpoint_y + endpoint_z) / 2

    endpoint_y_simple = hy + hwz - hwuy - hwvz + hwuv
    endpoint_z_simple = hz + hwy - hwuy - hwvz + hwuv
    if abs(endpoint_y - endpoint_y_simple) > D("1e-90"):
        raise AssertionError("Y entropy identity")
    if abs(endpoint_z - endpoint_z_simple) > D("1e-90"):
        raise AssertionError("Z entropy identity")
    total = sum(marginal(p, ()), F(0))
    if total != 1:
        raise AssertionError(total)
    print(name, "exact_simplex", total)
    for key, value in (("I(W;Y)", iwy), ("I(W;Z)", iwz),
                       ("I(U;Y|W)", iuyw), ("I(V;Z|W)", ivzw),
                       ("I(U;V|W)", iuvw), ("J", j),
                       ("Y_endpoint", endpoint_y), ("Z_endpoint", endpoint_z),
                       ("Lhalf", half)):
        print(name, key, format(value, ".75g"))
    correlation_ledger(name, p, half)
    return half


def main():
    digest, raw, reflected = exact_laws()
    print("source", SOURCE, "sha256", digest, "mapping", MAPPING)
    raw_half = audit("raw", raw)
    reflected_half = audit("reflected", reflected)
    if not reflected_half > raw_half:
        raise AssertionError("expected common-layer improvement")
    print("PASS: exact masses and independent entropy identities agree")


if __name__ == "__main__":
    main()
