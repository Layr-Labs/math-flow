#!/usr/bin/env python3
"""Exact audit of the invariant representation of the frontier dual face."""

from fractions import Fraction as F


A, B, C = range(3)
CONST, W, U, V = range(4)
Y, Z, G, K = range(4)

KINDS = {
    "W": ((CONST, 1), (W, -1)),
    "U|W": ((W, 1), (U, -1)),
    "V|W": ((W, 1), (V, -1)),
    "UW": ((CONST, 1), (U, -1)),
    "VW": ((CONST, 1), (V, -1)),
    "X|UW": ((U, 1),),
    "X|VW": ((V, 1),),
}


def add_terms(*blocks):
    result = []
    for block in blocks:
        result.extend(block)
    return result


R1_C_BASE = [
    (C, "W", Z, 1), (A, "U|W", Y, 1),
    (A, "W", G, 1), (B, "W", G, -1),
    (B, "W", K, 1), (C, "W", K, -1),
]
R1_INC = [(B, "UW", G, 1), (A, "UW", G, -1)]

R2_C_BASE = [(C, "W", Z, 1), (C, "V|W", Z, 1)]
R2_A_BASE = [
    (A, "W", Y, 1), (C, "V|W", Z, 1),
    (C, "W", K, 1), (B, "W", K, -1),
    (B, "W", G, 1), (A, "W", G, -1),
]
R2_INC = [(B, "VW", K, 1), (C, "VW", K, -1)]

K_COMMON = [
    (C, "UW", K, 1), (B, "UW", K, -1),
    (B, "UW", G, 1), (A, "UW", G, -1),
    (A, "U|W", Y, 1), (C, "X|UW", Z, 1),
]
L_COMMON = [
    (A, "VW", G, 1), (B, "VW", G, -1),
    (B, "VW", K, 1), (C, "VW", K, -1),
    (C, "V|W", Z, 1), (A, "X|VW", Y, 1),
]

ROWS = {
    "r1_c_1": (1, 0, add_terms(R1_C_BASE, R1_INC)),
    "r2_c_1": (0, 1, add_terms(R2_C_BASE, R2_INC)),
    "r2_a_1": (0, 1, add_terms(R2_A_BASE, R2_INC)),
    "19k_a": (1, 1, add_terms(K_COMMON, [(A, "W", Y, 1)])),
    "19l_a": (1, 1, add_terms(L_COMMON, [
        (A, "W", Y, 1),
        (C, "W", K, 1), (B, "W", K, -1),
        (B, "W", G, 1), (A, "W", G, -1),
    ])),
    "19l_c": (1, 1, add_terms(L_COMMON, [(C, "W", Z, 1)])),
    "19m": (1, 1, [
        (A, "W", Y, 1), (A, "U|W", Y, 1),
        (C, "V|W", Z, 1),
        (B, "UW", G, 1), (A, "UW", G, -1),
        (C, "V|W", K, -1), (B, "X|UW", K, 1),
    ]),
    "19o": (1, 1, [
        (C, "W", Z, 1), (A, "U|W", Y, 1),
        (C, "V|W", Z, 1),
        (B, "VW", K, 1), (C, "VW", K, -1),
        (A, "U|W", G, -1), (B, "X|VW", G, 1),
    ]),
    "final_a_rml": (0, 0, [
        (A, "U|W", Y, 1), (A, "U|W", G, -1),
        (A, "X|VW", Y, -1), (A, "X|VW", G, 1),
    ]),
    "final_c_rml": (0, 0, [
        (C, "V|W", Z, 1), (C, "V|W", K, -1),
        (C, "X|UW", Z, -1), (C, "X|UW", K, 1),
    ]),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def poly(a=0, b=0):
    return (F(a), F(b))


def padd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def pneg(x):
    return (-x[0], -x[1])


def pscale(x, scalar):
    scalar = F(scalar)
    return (scalar * x[0], scalar * x[1])


ZERO = poly()
EPS = poly(0, 1)
HALF_MINUS_HALF_EPS = poly(F(1, 2), F(-1, 2))
HALF_MINUS_THREE_HALVES_EPS = poly(F(1, 2), F(-3, 2))

FRONTIER = {
    "r1_c_1": EPS,
    "r2_c_1": EPS,
    "19l_a": EPS,
    "19m": HALF_MINUS_HALF_EPS,
    "19o": HALF_MINUS_THREE_HALVES_EPS,
    "final_a_rml": EPS,
}

INVARIANT = {
    "r1_c_1": EPS,
    "r2_a_1": EPS,
    "19k_a": HALF_MINUS_HALF_EPS,
    "19l_c": HALF_MINUS_HALF_EPS,
    "final_a_rml": HALF_MINUS_HALF_EPS,
    "final_c_rml": HALF_MINUS_HALF_EPS,
}


def row_tensor(terms):
    tensor = [[[[F(0) for _ in range(4)] for _ in range(4)]
               for _ in range(3)]][0]
    for group, kind, channel, sign in terms:
        for level, coefficient in KINDS[kind]:
            tensor[group][level][channel] += F(sign * coefficient)
    return tensor


TENSORS = {name: row_tensor(data[2]) for name, data in ROWS.items()}


def combination(weights):
    result = [[[ZERO for _ in range(4)] for _ in range(4)]
              for _ in range(3)]
    for name, weight in weights.items():
        require(name in ROWS, "unknown row " + name)
        tensor = TENSORS[name]
        for group in range(3):
            for level in range(4):
                for channel in range(4):
                    result[group][level][channel] = padd(
                        result[group][level][channel],
                        pscale(weight, tensor[group][level][channel]),
                    )
    return result


def rate_vector(weights):
    answer = [ZERO, ZERO]
    for name, weight in weights.items():
        answer[0] = padd(answer[0], pscale(weight, ROWS[name][0]))
        answer[1] = padd(answer[1], pscale(weight, ROWS[name][1]))
    return tuple(answer)


def main():
    one = poly(1, 0)
    require(rate_vector(FRONTIER) == (one, one),
            "frontier rate normalization failed")
    require(rate_vector(INVARIANT) == (one, one),
            "invariant rate normalization failed")

    all_pairs = [
        ("common_0", "common_3"), ("common_1", "common_4"),
        ("common_2", "common_5"), ("r1_a_0", "r2_c_0"),
        ("r1_a_1", "r2_c_1"), ("r1_a_2", "r2_c_2"),
        ("r1_c_0", "r2_a_0"), ("r1_c_1", "r2_a_1"),
        ("r1_c_2", "r2_a_2"), ("19k_a", "19l_c"),
        ("19k_c", "19l_a"), ("19m", "19o"),
        ("19n", "19p"), ("final_c_left", "final_a_left"),
        ("final_c_rml", "final_a_rml"),
    ]
    for left, right in all_pairs:
        require(INVARIANT.get(left, ZERO) == INVARIANT.get(right, ZERO),
                "skew-pair mismatch: " + left + ", " + right)

    # In the accepted P1,...,P15 ordering, the only nonzero pair weights are
    # t3=L, t9=epsilon, t15=L.  Equation (14) of the rank-eight quotient then
    # gives (sB,sC,sD,sE,sN0,sN1,sF0,sF1)=(L,0,e,0,0,0,0,L).
    quotient = (
        HALF_MINUS_HALF_EPS, ZERO, EPS, ZERO,
        ZERO, ZERO, ZERO, HALF_MINUS_HALF_EPS,
    )
    normalization = padd(pscale(quotient[0], 2), quotient[2])
    require(normalization == one, "rank-eight quotient normalization failed")

    first = combination(FRONTIER)
    second = combination(INVARIANT)
    difference = [[[padd(first[g][l][d], pneg(second[g][l][d]))
                    for d in range(4)] for l in range(4)]
                  for g in range(3)]

    for group in range(3):
        for level in (W, U, V):
            for channel in range(4):
                require(difference[group][level][channel] == ZERO,
                        "nonconstant tensor mismatch")

    expected = {
        (A, G): poly(F(-1, 2), F(3, 2)),
        (B, G): poly(F(1, 2), F(-3, 2)),
        (B, K): poly(F(1, 2), F(-1, 2)),
        (C, K): poly(F(-1, 2), F(1, 2)),
    }
    for group in range(3):
        for channel in range(4):
            require(difference[group][CONST][channel]
                    == expected.get((group, channel), ZERO),
                    "unexpected constant residual")

    for channel in range(4):
        total = ZERO
        for group in range(3):
            total = padd(total, difference[group][CONST][channel])
        require(total == ZERO, "group-summed constant did not cancel")

    # Endpoint checks certify nonnegativity of every displayed affine weight
    # throughout 0 <= epsilon <= 1/3.
    endpoints = (F(0), F(1, 3))
    for family_name, weights in (("frontier", FRONTIER),
                                 ("invariant", INVARIANT)):
        for row, weight in weights.items():
            for epsilon in endpoints:
                value = weight[0] + epsilon * weight[1]
                require(value >= 0,
                        family_name + " negative weight on " + row)

    print("exact row expansion: passed")
    print("rate normalizations: (1,1) and (1,1)")
    print("new weights: skew-invariant across all 15 row pairs")
    print("rank-eight quotient: ((1-e)/2,0,e,0,0,0,0,(1-e)/2)")
    print("nonconstant tensors: identical")
    print("group-summed constant tensors: identical")
    print("functional identity: verified for symbolic epsilon")


if __name__ == "__main__":
    main()
