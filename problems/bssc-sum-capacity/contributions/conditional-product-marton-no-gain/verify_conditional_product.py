#!/usr/bin/env python3
"""Mechanical corroboration for the Marton entropy identities.

The universal theorem is analytic.  This deterministic standard-library
script checks its finite-alphabet entropy bookkeeping on fixed-seed examples
and verifies the exact half-skew BSSC receiver relabeling.  It also checks the
exact total-correlation ledger on arbitrary correlated tuple laws.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import log2
from random import Random
from typing import Hashable, Iterable


TOL = 2e-11

Y_CHANNEL = (
    (Fraction(1, 2), Fraction(1, 2)),
    (Fraction(0), Fraction(1)),
)
Z_CHANNEL = (
    (Fraction(1), Fraction(0)),
    (Fraction(1, 2), Fraction(1, 2)),
)


def entropy(joint: dict[tuple[Hashable, ...], float], positions: Iterable[int]) -> float:
    selected = tuple(positions)
    marginal: dict[tuple[Hashable, ...], float] = defaultdict(float)
    for outcome, probability in joint.items():
        marginal[tuple(outcome[i] for i in selected)] += probability
    return -sum(p * log2(p) for p in marginal.values() if p > 0.0)


def mutual_information(
    joint: dict[tuple[Hashable, ...], float],
    left: Iterable[int],
    right: Iterable[int],
) -> float:
    left = tuple(left)
    right = tuple(right)
    return entropy(joint, left) + entropy(joint, right) - entropy(joint, left + right)


def conditional_mutual_information(
    joint: dict[tuple[Hashable, ...], float],
    left: Iterable[int],
    right: Iterable[int],
    given: Iterable[int],
) -> float:
    left = tuple(left)
    right = tuple(right)
    given = tuple(given)
    return (
        entropy(joint, left + given)
        + entropy(joint, right + given)
        - entropy(joint, given)
        - entropy(joint, left + right + given)
    )


def conditional_entropy(
    joint: dict[tuple[Hashable, ...], float],
    target: Iterable[int],
    given: Iterable[int] = (),
) -> float:
    target = tuple(target)
    given = tuple(given)
    if not given:
        return entropy(joint, target)
    return entropy(joint, target + given) - entropy(joint, given)


def total_correlation(
    joint: dict[tuple[Hashable, ...], float],
    coordinate_groups: Iterable[Iterable[int]],
    given: Iterable[int] = (),
) -> float:
    groups = tuple(tuple(group) for group in coordinate_groups)
    flattened = tuple(position for group in groups for position in group)
    return sum(conditional_entropy(joint, group, given) for group in groups) - (
        conditional_entropy(joint, flattened, given)
    )


def normalized_weights(rng: Random, count: int) -> tuple[float, ...]:
    weights = [rng.randrange(1, 100) for _ in range(count)]
    total = sum(weights)
    return tuple(weight / total for weight in weights)


PACKETS = tuple((u, v, x) for u in range(2) for v in range(2) for x in range(2))


def random_one_letter_law(
    rng: Random,
) -> tuple[dict[Hashable, float], dict[Hashable, dict[tuple[int, int, int], float]]]:
    w_values: tuple[Hashable, ...] = (0, 1)
    p_w_values = normalized_weights(rng, len(w_values))
    p_w = dict(zip(w_values, p_w_values, strict=True))
    conditionals: dict[Hashable, dict[tuple[int, int, int], float]] = {}
    for w in w_values:
        probabilities = normalized_weights(rng, len(PACKETS))
        conditionals[w] = dict(zip(PACKETS, probabilities, strict=True))
    return p_w, conditionals


def build_two_letter_base(
    p_w: dict[Hashable, float],
    first: dict[Hashable, dict[tuple[int, int, int], float]],
    second: dict[Hashable, dict[tuple[int, int, int], float]],
) -> dict[tuple[Hashable, ...], float]:
    # Tuple order: w,u1,v1,x1,u2,v2,x2.
    joint: dict[tuple[Hashable, ...], float] = {}
    for w, pw in p_w.items():
        for (u1, v1, x1), p1 in first[w].items():
            for (u2, v2, x2), p2 in second[w].items():
                joint[(w, u1, v1, x1, u2, v2, x2)] = pw * p1 * p2
    return joint


def random_correlated_tuple_base(
    rng: Random,
) -> dict[tuple[Hashable, ...], float]:
    """Build an arbitrary p(w,u1,v1,x1,u2,v2,x2)."""

    w_values: tuple[Hashable, ...] = (0, 1)
    p_w = dict(
        zip(w_values, normalized_weights(rng, len(w_values)), strict=True)
    )
    tuple_values = tuple(first + second for first in PACKETS for second in PACKETS)
    joint: dict[tuple[Hashable, ...], float] = {}
    for w, pw in p_w.items():
        conditional = dict(
            zip(
                tuple_values,
                normalized_weights(rng, len(tuple_values)),
                strict=True,
            )
        )
        for packet_pair, probability in conditional.items():
            joint[(w,) + packet_pair] = pw * probability
    return joint


def append_outputs(
    base: dict[tuple[Hashable, ...], float],
    channel: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> dict[tuple[Hashable, ...], float]:
    # Output tuple order: base followed by o1,o2.
    joint: dict[tuple[Hashable, ...], float] = {}
    for outcome, probability in base.items():
        x1, x2 = int(outcome[3]), int(outcome[6])
        for o1 in range(2):
            for o2 in range(2):
                p = probability * float(channel[x1][o1] * channel[x2][o2])
                if p:
                    joint[outcome + (o1, o2)] = p
    return joint


def append_one_output(
    base: dict[tuple[Hashable, ...], float],
    channel: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> dict[tuple[Hashable, ...], float]:
    # Input tuple order: w,u,v,x; output is appended at position 4.
    joint: dict[tuple[Hashable, ...], float] = {}
    for outcome, probability in base.items():
        x = int(outcome[3])
        for output in range(2):
            p = probability * float(channel[x][output])
            if p:
                joint[outcome + (output,)] = p
    return joint


def two_letter_terms(
    base: dict[tuple[Hashable, ...], float],
) -> dict[str, float]:
    y_joint = append_outputs(base, Y_CHANNEL)
    z_joint = append_outputs(base, Z_CHANNEL)

    common_y = mutual_information(y_joint, (0,), (7, 8))
    common_z = mutual_information(z_joint, (0,), (7, 8))
    common_y_sum = sum(mutual_information(y_joint, (0,), (i,)) for i in (7, 8))
    common_z_sum = sum(mutual_information(z_joint, (0,), (i,)) for i in (7, 8))

    u_y = conditional_mutual_information(y_joint, (1, 4), (7, 8), (0,))
    u_y_sum = (
        conditional_mutual_information(y_joint, (1,), (7,), (0,))
        + conditional_mutual_information(y_joint, (4,), (8,), (0,))
    )
    v_z = conditional_mutual_information(z_joint, (2, 5), (7, 8), (0,))
    v_z_sum = (
        conditional_mutual_information(z_joint, (2,), (7,), (0,))
        + conditional_mutual_information(z_joint, (5,), (8,), (0,))
    )
    u_v = conditional_mutual_information(base, (1, 4), (2, 5), (0,))
    u_v_sum = (
        conditional_mutual_information(base, (1,), (2,), (0,))
        + conditional_mutual_information(base, (4,), (5,), (0,))
    )

    marton = min(common_y, common_z) + u_y + v_z - u_v
    affine_half = (common_y + common_z) / 2 + u_y + v_z - u_v
    coordinate_sum = (
        (common_y_sum + common_z_sum) / 2 + u_y_sum + v_z_sum - u_v_sum
    )
    return {
        "common_y": common_y,
        "common_z": common_z,
        "common_y_sum": common_y_sum,
        "common_z_sum": common_z_sum,
        "u_y": u_y,
        "u_y_sum": u_y_sum,
        "v_z": v_z,
        "v_z_sum": v_z_sum,
        "u_v": u_v,
        "u_v_sum": u_v_sum,
        "marton": marton,
        "affine_half": affine_half,
        "coordinate_sum": coordinate_sum,
    }


def correlation_ledger_terms(
    base: dict[tuple[Hashable, ...], float],
) -> dict[str, float]:
    """Evaluate both sides of the exact two-letter residual identity."""

    y_joint = append_outputs(base, Y_CHANNEL)
    z_joint = append_outputs(base, Z_CHANNEL)
    marton_terms = two_letter_terms(base)

    tc_u_w = total_correlation(base, ((1,), (4,)), (0,))
    tc_v_w = total_correlation(base, ((2,), (5,)), (0,))
    tc_y_w = total_correlation(y_joint, ((7,), (8,)), (0,))
    tc_z_w = total_correlation(z_joint, ((7,), (8,)), (0,))
    tc_y = total_correlation(y_joint, ((7,), (8,)))
    tc_z = total_correlation(z_joint, ((7,), (8,)))

    g_u_y = (
        conditional_entropy(y_joint, (7,), (1, 0))
        + conditional_entropy(y_joint, (8,), (4, 0))
        - conditional_entropy(y_joint, (7, 8), (1, 4, 0))
    )
    g_v_z = (
        conditional_entropy(z_joint, (7,), (2, 0))
        + conditional_entropy(z_joint, (8,), (5, 0))
        - conditional_entropy(z_joint, (7, 8), (2, 5, 0))
    )
    g_u_v = (
        conditional_entropy(base, (1,), (2, 0))
        + conditional_entropy(base, (4,), (5, 0))
        - conditional_entropy(base, (1, 4), (2, 5, 0))
    )
    g_v_u = (
        conditional_entropy(base, (2,), (1, 0))
        + conditional_entropy(base, (5,), (4, 0))
        - conditional_entropy(base, (2, 5), (1, 4, 0))
    )

    residual = (
        tc_u_w
        + g_u_y
        + g_v_z
        - g_u_v
        - 0.5 * (tc_y_w + tc_y + tc_z_w + tc_z)
    )
    return {
        "delta": marton_terms["affine_half"] - marton_terms["coordinate_sum"],
        "residual": residual,
        "tc_u_w": tc_u_w,
        "tc_v_w": tc_v_w,
        "tc_y_w": tc_y_w,
        "tc_z_w": tc_z_w,
        "tc_y": tc_y,
        "tc_z": tc_z,
        "g_u_y": g_u_y,
        "g_v_z": g_v_z,
        "g_u_v": g_u_v,
        "g_v_u": g_v_u,
    }


def one_letter_marton(
    p_w: dict[Hashable, float],
    conditional: dict[Hashable, dict[tuple[int, int, int], float]],
) -> float:
    base: dict[tuple[Hashable, ...], float] = {}
    for w, pw in p_w.items():
        for (u, v, x), pc in conditional[w].items():
            base[(w, u, v, x)] = pw * pc
    y_joint = append_one_output(base, Y_CHANNEL)
    z_joint = append_one_output(base, Z_CHANNEL)
    common_y = mutual_information(y_joint, (0,), (4,))
    common_z = mutual_information(z_joint, (0,), (4,))
    u_y = conditional_mutual_information(y_joint, (1,), (4,), (0,))
    v_z = conditional_mutual_information(z_joint, (2,), (4,), (0,))
    u_v = conditional_mutual_information(base, (1,), (2,), (0,))
    return min(common_y, common_z) + u_y + v_z - u_v


def assert_close(left: float, right: float, label: str) -> None:
    if abs(left - right) > TOL:
        raise AssertionError(f"{label}: {left!r} != {right!r}")


def verify_skew() -> None:
    for x in range(2):
        for output in range(2):
            assert Y_CHANNEL[1 - x][output] == Z_CHANNEL[x][1 - output]
            assert Z_CHANNEL[1 - x][output] == Y_CHANNEL[x][1 - output]


def verify_random_conditional_products() -> None:
    rng = Random(260819869)
    for trial in range(24):
        p_w, first = random_one_letter_law(rng)
        _, second = random_one_letter_law(rng)
        base = build_two_letter_base(p_w, first, second)
        terms = two_letter_terms(base)

        assert_close(terms["u_y"], terms["u_y_sum"], f"trial {trial}: U/Y")
        assert_close(terms["v_z"], terms["v_z_sum"], f"trial {trial}: V/Z")
        assert_close(terms["u_v"], terms["u_v_sum"], f"trial {trial}: U/V")
        assert terms["common_y"] <= terms["common_y_sum"] + TOL
        assert terms["common_z"] <= terms["common_z_sum"] + TOL
        assert terms["marton"] <= terms["affine_half"] + TOL
        assert terms["affine_half"] <= terms["coordinate_sum"] + TOL

        ledger = correlation_ledger_terms(base)
        assert_close(ledger["delta"], ledger["residual"], f"trial {trial}: ledger")
        for label in (
            "tc_u_w",
            "tc_y_w",
            "tc_z_w",
            "g_u_y",
            "g_v_z",
            "g_u_v",
        ):
            assert_close(ledger[label], 0.0, f"trial {trial}: product {label}")
        expected_delta = -0.5 * (ledger["tc_y"] + ledger["tc_z"])
        assert_close(ledger["delta"], expected_delta, f"trial {trial}: deficit")


def verify_correlated_ledger() -> None:
    rng = Random(110260819869)
    largest_delta = 0.0
    for trial in range(24):
        base = random_correlated_tuple_base(rng)
        ledger = correlation_ledger_terms(base)
        assert_close(
            ledger["delta"],
            ledger["residual"],
            f"correlated trial {trial}: ledger",
        )
        assert_close(
            ledger["tc_u_w"] - ledger["g_u_v"],
            ledger["tc_v_w"] - ledger["g_v_u"],
            f"correlated trial {trial}: symmetric penalty",
        )
        for label in (
            "tc_u_w",
            "tc_v_w",
            "tc_y_w",
            "tc_z_w",
            "tc_y",
            "tc_z",
            "g_u_y",
            "g_v_z",
            "g_u_v",
            "g_v_u",
        ):
            if ledger[label] < -TOL:
                raise AssertionError(
                    f"correlated trial {trial}: negative {label}={ledger[label]!r}"
                )
        largest_delta = max(largest_delta, abs(ledger["delta"]))
    if largest_delta < 1e-6:
        raise AssertionError("correlated ledger trials were numerically trivial")


def verify_independent_copy_equality() -> None:
    rng = Random(10011468)
    p_w_one, conditional_one = random_one_letter_law(rng)
    one = one_letter_marton(p_w_one, conditional_one)

    p_w_pair: dict[tuple[Hashable, Hashable], float] = {}
    first: dict[tuple[Hashable, Hashable], dict[tuple[int, int, int], float]] = {}
    second: dict[tuple[Hashable, Hashable], dict[tuple[int, int, int], float]] = {}
    for w1, p1 in p_w_one.items():
        for w2, p2 in p_w_one.items():
            pair = (w1, w2)
            p_w_pair[pair] = p1 * p2
            first[pair] = conditional_one[w1]
            second[pair] = conditional_one[w2]

    base = build_two_letter_base(p_w_pair, first, second)
    two = two_letter_terms(base)["marton"]
    assert_close(two, 2 * one, "independent-copy Marton equality")


def main() -> None:
    verify_skew()
    verify_random_conditional_products()
    verify_correlated_ledger()
    verify_independent_copy_equality()
    print("PASS: exact BSSC receiver-skew relabeling")
    print("PASS: conditional-product entropy identities and common-term bounds")
    print("PASS: exact total-correlation ledger on correlated tuple laws")
    print("PASS: independent-copy Marton equality")


if __name__ == "__main__":
    main()
