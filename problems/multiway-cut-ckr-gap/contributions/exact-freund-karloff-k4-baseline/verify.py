#!/usr/bin/env python3
"""Exact verifier for the k=4 Freund--Karloff baseline instance.

Only the Python standard library is used.  All numerical work is performed
with fractions.Fraction; there is no floating-point LP solve.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def midpoint_pair(name: str) -> tuple[int, int]:
    if len(name) != 3 or not name.startswith("m"):
        raise ValueError(f"invalid midpoint name: {name!r}")
    i, j = int(name[1]), int(name[2])
    if not 1 <= i < j:
        raise ValueError(f"noncanonical midpoint name: {name!r}")
    return i, j


def expected_family(k: int):
    terminals = tuple(f"t{i}" for i in range(1, k + 1))
    midpoints = tuple(
        f"m{i}{j}" for i in range(1, k + 1) for j in range(i + 1, k + 1)
    )
    outer_weight = Fraction(1, (k - 1) ** 2)
    inner_weight = Fraction(3, 2 * k * (k - 1) ** 2)

    edges: dict[frozenset[str], Fraction] = {}
    for name in midpoints:
        i, j = midpoint_pair(name)
        edges[frozenset((f"t{i}", name))] = outer_weight
        edges[frozenset((f"t{j}", name))] = outer_weight
    for i, j, ell in itertools.combinations(range(1, k + 1), 3):
        names = (f"m{i}{j}", f"m{i}{ell}", f"m{j}{ell}")
        for u, v in itertools.combinations(names, 2):
            edges[frozenset((u, v))] = inner_weight

    embedding: dict[str, tuple[Fraction, ...]] = {}
    for i, terminal in enumerate(terminals):
        embedding[terminal] = tuple(
            Fraction(int(i == coordinate)) for coordinate in range(k)
        )
    for name in midpoints:
        i, j = midpoint_pair(name)
        embedding[name] = tuple(
            Fraction(1, 2) if coordinate + 1 in (i, j) else Fraction(0)
            for coordinate in range(k)
        )
    return terminals, midpoints, edges, embedding


def load_and_validate_instance(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schemaVersion") != 1:
        raise AssertionError("schemaVersion must be 1")
    if raw.get("problemId") != "multiway-cut-ckr-gap":
        raise AssertionError("wrong problemId")
    k = raw.get("k")
    if k != 4:
        raise AssertionError("this committed certificate must have k=4")

    terminals, midpoints, expected_edges, expected_embedding = expected_family(k)
    vertices = tuple(raw.get("vertices", ()))
    if vertices != terminals + midpoints:
        raise AssertionError("vertices are missing, duplicated, or out of canonical order")
    if tuple(raw.get("terminals", ())) != terminals:
        raise AssertionError("terminal list mismatch")

    edges: dict[frozenset[str], Fraction] = {}
    for record in raw.get("edges", ()):
        if set(record) != {"u", "v", "weight"}:
            raise AssertionError(f"malformed edge record: {record!r}")
        u, v = record["u"], record["v"]
        if u == v or u not in vertices or v not in vertices:
            raise AssertionError(f"invalid edge endpoints: {u!r}, {v!r}")
        key = frozenset((u, v))
        if key in edges:
            raise AssertionError(f"duplicate undirected edge: {u!r}, {v!r}")
        weight = Fraction(record["weight"])
        if weight < 0:
            raise AssertionError("edge weights must be nonnegative")
        edges[key] = weight
    if edges != expected_edges:
        raise AssertionError("edge set or rational weights do not match H_4")

    raw_embedding = raw.get("embedding", {})
    if set(raw_embedding) != set(vertices):
        raise AssertionError("embedding domain does not equal the vertex set")
    embedding = {
        vertex: tuple(Fraction(value) for value in raw_embedding[vertex])
        for vertex in vertices
    }
    for vertex, vector in embedding.items():
        if len(vector) != k or any(value < 0 for value in vector):
            raise AssertionError(f"{vertex} is not embedded in Delta_{k}")
        if sum(vector) != 1:
            raise AssertionError(f"coordinates for {vertex} do not sum to one")
    if embedding != expected_embedding:
        raise AssertionError("embedding is not the canonical midpoint embedding")

    claims = {key: Fraction(value) for key, value in raw.get("claimedValues", {}).items()}
    expected_claims = {
        "ckr": Fraction(11, 12),
        "integralOptimum": Fraction(1),
        "ratio": Fraction(12, 11),
    }
    if claims != expected_claims:
        raise AssertionError("claimed exact values mismatch")
    return k, terminals, midpoints, edges, embedding, claims


def half_l1(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def embedding_cost(edges, embedding) -> Fraction:
    return sum(
        weight * half_l1(embedding[u], embedding[v])
        for endpoints, weight in edges.items()
        for u, v in [tuple(endpoints)]
    )


def verify_lp_subgradient(k, terminals, midpoints, edges, embedding) -> Fraction:
    """Check an exact first-order optimality certificate at the embedding.

    On a zero coordinate difference of an outer edge, the subgradient with
    respect to the midpoint endpoint is chosen as +3/4.  On every zero
    difference of an inner edge it is chosen as 0.  Nonzero differences force
    their usual signs.  The resulting objective subgradient is constant across
    all k coordinates at every midpoint, hence orthogonal to every feasible
    simplex direction.  Convexity then proves global LP optimality.
    """

    terminal_set = set(terminals)
    gradient = {name: [Fraction(0) for _ in range(k)] for name in midpoints}

    for endpoints, weight in edges.items():
        u, v = tuple(endpoints)
        is_outer = (u in terminal_set) ^ (v in terminal_set)
        midpoint = v if u in terminal_set else u if v in terminal_set else None
        midpoint_support = set(midpoint_pair(midpoint)) if is_outer else set()

        for coordinate in range(k):
            difference = embedding[u][coordinate] - embedding[v][coordinate]
            if difference > 0:
                sign = Fraction(1)
            elif difference < 0:
                sign = Fraction(-1)
            elif is_outer and coordinate + 1 not in midpoint_support:
                # Choose the sign so the derivative at the midpoint is +3/4.
                sign = Fraction(3, 4) if u == midpoint else Fraction(-3, 4)
            else:
                sign = Fraction(0)

            if not -1 <= sign <= 1:
                raise AssertionError("invalid absolute-value subgradient")
            if difference != 0 and sign * difference != abs(difference):
                raise AssertionError("subgradient does not match a nonzero difference")
            if u in gradient:
                gradient[u][coordinate] += weight * sign / 2
            if v in gradient:
                gradient[v][coordinate] -= weight * sign / 2

    expected_multiplier = Fraction(3 * (k - 2), 4 * k * (k - 1) ** 2)
    for vertex, row in gradient.items():
        if any(value != expected_multiplier for value in row):
            raise AssertionError(f"stationarity failed at {vertex}: {row!r}")

    value = embedding_cost(edges, embedding)
    expected_value = Fraction(7 * k - 6, 8 * (k - 1))
    if value != expected_value:
        raise AssertionError(f"unexpected canonical objective: {value}")
    return value


def enumerate_integral_cuts(k, terminals, midpoints, edges):
    labels = {terminal: i for i, terminal in enumerate(terminals)}
    optimum = None
    minimizers = 0
    cost_histogram: Counter[Fraction] = Counter()
    assignments = 0

    for choices in itertools.product(range(k), repeat=len(midpoints)):
        assignments += 1
        labels.update(zip(midpoints, choices))
        cost = sum(
            weight
            for endpoints, weight in edges.items()
            for u, v in [tuple(endpoints)]
            if labels[u] != labels[v]
        )
        cost_histogram[cost] += 1
        if optimum is None or cost < optimum:
            optimum = cost
            minimizers = 1
        elif cost == optimum:
            minimizers += 1

    return assignments, optimum, minimizers, cost_histogram


def enumerate_base_lemma():
    """Replay the 64-labeling local lemma used in the family proof."""

    midpoint_names = ("m12", "m13", "m23")
    endpoint_sets = ({1, 2}, {1, 3}, {2, 3})
    unrestricted_minimum = None
    nonopposite_minimum = None

    for choices in itertools.product((1, 2, 3, 4), repeat=3):
        labels = {"t1": 1, "t2": 2, "t3": 3}
        labels.update(zip(midpoint_names, choices))
        outer_crossings = sum(
            labels[f"m{i}{j}"] != endpoint
            for i, j in ((1, 2), (1, 3), (2, 3))
            for endpoint in (i, j)
        )
        inner_crossings = sum(
            labels[u] != labels[v]
            for u, v in itertools.combinations(midpoint_names, 2)
        )
        cost = Fraction(outer_crossings, 6) + Fraction(inner_crossings, 4)
        unrestricted_minimum = (
            cost if unrestricted_minimum is None else min(unrestricted_minimum, cost)
        )
        if all(label in support | {4} for label, support in zip(choices, endpoint_sets)):
            nonopposite_minimum = (
                cost if nonopposite_minimum is None else min(nonopposite_minimum, cost)
            )

    if unrestricted_minimum != Fraction(2, 3):
        raise AssertionError(f"base unrestricted minimum is {unrestricted_minimum}")
    if nonopposite_minimum != Fraction(1):
        raise AssertionError(f"base non-opposite minimum is {nonopposite_minimum}")
    return unrestricted_minimum, nonopposite_minimum


def main() -> int:
    instance_path = HERE / "instance-k4.json"
    k, terminals, midpoints, edges, embedding, claims = load_and_validate_instance(
        instance_path
    )
    ckr_value = verify_lp_subgradient(k, terminals, midpoints, edges, embedding)
    assignments, integral_optimum, minimizers, histogram = enumerate_integral_cuts(
        k, terminals, midpoints, edges
    )
    unrestricted, nonopposite = enumerate_base_lemma()

    if integral_optimum != claims["integralOptimum"]:
        raise AssertionError(f"integral optimum is {integral_optimum}")
    if ckr_value != claims["ckr"]:
        raise AssertionError(f"CKR optimum is {ckr_value}")
    ratio = integral_optimum / ckr_value
    if ratio != claims["ratio"]:
        raise AssertionError(f"integrality ratio is {ratio}")
    if sum(histogram.values()) != assignments:
        raise AssertionError("integral cost histogram lost assignments")

    print(f"instance: k={k}, |V|={len(terminals) + len(midpoints)}, |E|={len(edges)}")
    print(f"base lemma: unrestricted={unrestricted}, non-opposite={nonopposite}")
    print(f"CKR optimum: {ckr_value} (exact subgradient certificate)")
    print(
        f"integral optimum: {integral_optimum} "
        f"({assignments} assignments, {minimizers} minimizers)"
    )
    print(f"integrality ratio: {ratio}")
    print("verification: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"verification: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
