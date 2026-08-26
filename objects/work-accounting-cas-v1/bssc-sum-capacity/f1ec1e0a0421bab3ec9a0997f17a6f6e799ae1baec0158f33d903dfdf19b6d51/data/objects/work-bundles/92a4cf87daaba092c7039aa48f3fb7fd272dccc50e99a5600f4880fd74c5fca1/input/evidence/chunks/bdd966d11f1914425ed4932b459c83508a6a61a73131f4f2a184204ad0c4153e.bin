#!/usr/bin/env python3
"""Numerical audit of the exact UV product-factorization identities.

This is corroboration, not a proof.  It uses only the Python standard library.
"""

from __future__ import annotations

from collections import defaultdict
import math
import random


TOL = 2.0e-11


def normalized(values):
    total = sum(values)
    return [value / total for value in values]


def random_factor_channel(rng):
    """Return W[x][y][z] for binary X,Y,Z, with strictly positive rows."""
    channel = []
    for _x in range(2):
        row = normalized([rng.random() + 0.1 for _ in range(4)])
        channel.append([[row[2 * y + z] for z in range(2)] for y in range(2)])
    return channel


def product_joint(p_ax, w1, w2):
    """Law of (A,X1,X2,Y1,Z1,Y2,Z2)."""
    joint = {}
    for (a, x1, x2), pin in p_ax.items():
        for y1 in range(2):
            for z1 in range(2):
                for y2 in range(2):
                    for z2 in range(2):
                        joint[(a, x1, x2, y1, z1, y2, z2)] = (
                            pin * w1[x1][y1][z1] * w2[x2][y2][z2]
                        )
    return joint


def project(key, indices):
    return tuple(key[index] for index in indices)


def conditional_mi(joint, left, right, given=()):
    """I(key[left]; key[right] | key[given]) in bits."""
    abc = defaultdict(float)
    ac = defaultdict(float)
    bc = defaultdict(float)
    c = defaultdict(float)
    for key, probability in joint.items():
        a_value = project(key, left)
        b_value = project(key, right)
        c_value = project(key, given)
        abc[(a_value, b_value, c_value)] += probability
        ac[(a_value, c_value)] += probability
        bc[(b_value, c_value)] += probability
        c[c_value] += probability
    result = 0.0
    for (a_value, b_value, c_value), probability in abc.items():
        if probability:
            ratio = probability * c[c_value] / (
                ac[(a_value, c_value)] * bc[(b_value, c_value)]
            )
            result += probability * math.log2(ratio)
    return result


def random_input_auxiliary(rng):
    values = normalized([rng.random() + 0.05 for _ in range(8)])
    return {
        (a, x1, x2): values[4 * a + 2 * x1 + x2]
        for a in range(2)
        for x1 in range(2)
        for x2 in range(2)
    }


def audit_chain_identities(seed, trials=100):
    rng = random.Random(seed)
    worst_markov = 0.0
    worst_identity = 0.0
    worst_lambda = 0.0
    worst_subadd_slack = float("inf")

    # Coordinate indices in product_joint's keys.
    a, x1, x2, y1, z1, y2, z2 = range(7)

    for _ in range(trials):
        w1 = random_factor_channel(rng)
        w2 = random_factor_channel(rng)
        joint = product_joint(random_input_auxiliary(rng), w1, w2)

        cross_1 = conditional_mi(joint, (y1,), (z2,), (x1, a))
        cross_2 = conditional_mi(joint, (z2,), (y1,), (x2, a))
        worst_markov = max(worst_markov, abs(cross_1), abs(cross_2))

        iy12 = conditional_mi(joint, (x1, x2), (y1, y2), (a,))
        iz12 = conditional_mi(joint, (x1, x2), (z1, z2), (a,))
        iy1 = conditional_mi(joint, (x1,), (y1,), (a, z2))
        iz1 = conditional_mi(joint, (x1,), (z1,), (a, z2))
        iy2 = conditional_mi(joint, (x2,), (y2,), (a, y1))
        iz2 = conditional_mi(joint, (x2,), (z2,), (a, y1))
        cross = conditional_mi(joint, (y1,), (z2,), (a,))

        error = (iy12 - iz12) - ((iy1 - iz1) + (iy2 - iz2))
        worst_identity = max(worst_identity, abs(error))

        for lam in (1.0, 1.7, 3.0):
            expected = (iy1 - lam * iz1) + (iy2 - lam * iz2)
            expected -= (lam - 1.0) * cross
            error_lam = (iy12 - lam * iz12) - expected
            worst_lambda = max(worst_lambda, abs(error_lam))

        iy12_plain = conditional_mi(joint, (x1, x2), (y1, y2))
        iy_sum = conditional_mi(joint, (x1,), (y1,))
        iy_sum += conditional_mi(joint, (x2,), (y2,))
        iz12_plain = conditional_mi(joint, (x1, x2), (z1, z2))
        iz_sum = conditional_mi(joint, (x1,), (z1,))
        iz_sum += conditional_mi(joint, (x2,), (z2,))
        worst_subadd_slack = min(
            worst_subadd_slack, iy_sum - iy12_plain, iz_sum - iz12_plain
        )

    assert worst_markov < TOL, worst_markov
    assert worst_identity < TOL, worst_identity
    assert worst_lambda < TOL, worst_lambda
    assert worst_subadd_slack > -TOL, worst_subadd_slack
    return worst_markov, worst_identity, worst_lambda, worst_subadd_slack


def channel_input_joint(prior, channel):
    return {
        (x, y, z): prior[x] * channel[x][y][z]
        for x in range(2)
        for y in range(2)
        for z in range(2)
    }


def t_factor(prior, channel):
    joint = channel_input_joint(prior, channel)
    return conditional_mi(joint, (0,), (1,)) - conditional_mi(joint, (0,), (2,))


def t_product(prior, w1, w2):
    # Reuse product_joint with a constant auxiliary.
    p_ax = {
        (0, x1, x2): prior[2 * x1 + x2]
        for x1 in range(2)
        for x2 in range(2)
    }
    joint = product_joint(p_ax, w1, w2)
    return conditional_mi(joint, (1, 2), (3, 5)) - conditional_mi(
        joint, (1, 2), (4, 6)
    )


def audit_product_mixtures(seed):
    rng = random.Random(seed)
    w1 = random_factor_channel(rng)
    w2 = random_factor_channel(rng)
    alpha = normalized([rng.random() + 0.1 for _ in range(3)])
    beta = normalized([rng.random() + 0.1 for _ in range(4)])
    post1 = [[1.0 - q, q] for q in [rng.random() for _ in alpha]]
    post2 = [[1.0 - q, q] for q in [rng.random() for _ in beta]]
    p1 = [sum(alpha[i] * post1[i][x] for i in range(3)) for x in range(2)]
    p2 = [sum(beta[j] * post2[j][x] for j in range(4)) for x in range(2)]

    barycenter = [0.0] * 4
    product_average = 0.0
    for i in range(3):
        for j in range(4):
            weight = alpha[i] * beta[j]
            prior = [
                post1[i][x1] * post2[j][x2]
                for x1 in range(2)
                for x2 in range(2)
            ]
            for x in range(4):
                barycenter[x] += weight * prior[x]
            product_average += weight * t_product(prior, w1, w2)

    target_barycenter = [p1[x1] * p2[x2] for x1 in range(2) for x2 in range(2)]
    factor_average = sum(
        alpha[i] * t_factor(post1[i], w1) for i in range(3)
    ) + sum(beta[j] * t_factor(post2[j], w2) for j in range(4))
    barycenter_error = max(
        abs(left - right) for left, right in zip(barycenter, target_barycenter)
    )
    value_error = abs(product_average - factor_average)
    assert barycenter_error < TOL, barycenter_error
    assert value_error < TOL, value_error
    return barycenter_error, value_error


def binary_entropy(q):
    if q == 0.0 or q == 1.0:
        return 0.0
    return -q * math.log2(q) - (1.0 - q) * math.log2(1.0 - q)


def bssc_t(q):
    iy = binary_entropy((1.0 - q) / 2.0) - (1.0 - q)
    iz = binary_entropy(q / 2.0) - q
    return iy - iz


def bssc_candidate_contact_witness():
    # At p=1/2, mix q=0 and q=4/5 for C[t], and q=1/5 and q=1 for C[-t].
    receiver_mi = binary_entropy(0.25) - 0.5
    envelope_witness = (5.0 / 8.0) * bssc_t(0.8)
    witness = receiver_mi + envelope_witness
    expected = 0.3725562489182657
    assert abs(witness - expected) < 2.0e-15, witness
    return witness, 2.0 * witness


def main():
    markov, identity, lambda_error, slack = audit_chain_identities(20260803)
    barycenter, product_value = audit_product_mixtures(20260804)
    one, two = bssc_candidate_contact_witness()
    print(f"max conditional-Markov residual: {markov:.3e}")
    print(f"max lambda=1 identity residual:  {identity:.3e}")
    print(f"max general-lambda residual:     {lambda_error:.3e}")
    print(f"minimum MI subadditivity slack:  {slack:.3e}")
    print(f"product-mixture barycenter error:{barycenter:.3e}")
    print(f"product-mixture value error:     {product_value:.3e}")
    print(f"BSSC candidate-contact witness: {one:.16f}; doubled: {two:.16f}")
    print("PASS")


if __name__ == "__main__":
    main()
