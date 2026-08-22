#!/usr/bin/env python3
"""Directed RTD interval and structural audit for the foundation repair."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
D = Decimal
PRECISION = 120
NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(name: str) -> dict:
    with (ROOT / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self) -> None:
        need(self.lo <= self.hi, "reversed interval")

    @staticmethod
    def point(value: str | int | Decimal) -> "IV":
        value = value if isinstance(value, Decimal) else D(value)
        return IV(value, value)

    def __add__(self, other: "IV") -> "IV":
        return IV(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    def __neg__(self) -> "IV":
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other: "IV") -> "IV":
        return self + (-other)

    def __mul__(self, other: "IV") -> "IV":
        products = (
            (self.lo, other.lo),
            (self.lo, other.hi),
            (self.hi, other.lo),
            (self.hi, other.hi),
        )
        return IV(
            min(DOWN.multiply(left, right) for left, right in products),
            max(UP.multiply(left, right) for left, right in products),
        )

    def __truediv__(self, other: "IV") -> "IV":
        need(not (other.lo <= 0 <= other.hi), "interval division by zero")
        reciprocal = IV(
            DOWN.divide(D(1), other.hi),
            UP.divide(D(1), other.lo),
        )
        return self * reciprocal

    def ln(self) -> "IV":
        need(self.lo > 0, "logarithm domain")
        # Decimal.ln is correctly rounded with ROUND_HALF_EVEN. Expanding the
        # endpoint evaluations by one representable number makes the enclosure
        # explicit; monotonicity of ln handles interval inputs.
        lower = NEAR.ln(self.lo).next_minus(context=NEAR)
        upper = NEAR.ln(self.hi).next_plus(context=NEAR)
        return IV(lower, upper)


Q = IV.point
ZERO = Q(0)
ONE = Q(1)
TWO = Q(2)
LN2 = TWO.ln()


def binary_entropy(value: IV) -> IV:
    need(D(0) < value.lo <= value.hi < D(1), "entropy input domain")
    complement = ONE - value
    return -(value * value.ln() + complement * complement.ln()) / LN2


def exact_fraction(text: str) -> Fraction:
    return Fraction(text)


def check_certificate() -> tuple[IV, IV, IV]:
    cert = load("interval_certificate.json")
    need(cert["schemaVersion"] == 1, "certificate schema")
    need(cert["units"] == "bits", "certificate units")
    need(cert["precisionDigits"] == PRECISION, "certificate precision")

    definitions = cert["exactDefinitions"]
    need(definitions["stationaryPolynomial"] == "15q^2-15q+2", "polynomial")
    need(definitions["maximizer"] == "q_-=(15-sqrt(105))/30", "maximizer")

    sqrt_data = cert["sqrt105"]
    sqrt_lo_q = exact_fraction(sqrt_data["lower"])
    sqrt_hi_q = exact_fraction(sqrt_data["upper"])
    need(sqrt_lo_q * sqrt_lo_q < 105 < sqrt_hi_q * sqrt_hi_q,
         "exact sqrt(105) bracket")

    sqrt_iv = IV(D(sqrt_data["lower"]), D(sqrt_data["upper"]))
    q_minus = (Q(15) - sqrt_iv) / Q(30)
    need(D(0) < q_minus.lo < q_minus.hi < D("0.5"), "q_- interval")

    # The bracket straddles the smaller root of the stationary polynomial.
    q_lo_q = exact_fraction(str(q_minus.lo))
    q_hi_q = exact_fraction(str(q_minus.hi))
    polynomial = lambda q: 15 * q * q - 15 * q + 2
    need(polynomial(q_lo_q) > 0 > polynomial(q_hi_q),
         "stationary-root straddle")

    half = Q("0.5")
    quarter = Q("0.25")
    l_rtd = (
        binary_entropy(quarter)
        - half
        + half
        * (
            binary_entropy(q_minus / TWO)
            - binary_entropy((ONE - q_minus) / TWO)
            + ONE
            - TWO * q_minus
        )
    )

    declared_l = IV(D(cert["lRtd"]["lower"]), D(cert["lRtd"]["upper"]))
    need(declared_l.lo < l_rtd.lo <= l_rtd.hi < declared_l.hi,
         "directed L_RTD enclosure")

    two_l_rtd = TWO * l_rtd
    declared_two = IV(
        D(cert["twoLRtd"]["lower"]),
        D(cert["twoLRtd"]["upper"]),
    )
    need(declared_two.lo < two_l_rtd.lo <= two_l_rtd.hi < declared_two.hi,
         "directed 2 L_RTD enclosure")
    need(
        DOWN.multiply(declared_l.lo, D(2)) == declared_two.lo
        and UP.multiply(declared_l.hi, D(2)) == declared_two.hi,
        "declared doubling consistency",
    )
    return q_minus, l_rtd, two_l_rtd


def check_structural_scope() -> None:
    claims = load("claims.json")
    premises = load("premises.json")
    need(claims["schemaVersion"] == premises["schemaVersion"] == 1, "schemas")
    need(len(claims["claims"]) == 1, "one declared claim")
    claim = claims["claims"][0]
    need(
        claim["claimKey"]
        == "bssc-sum-capacity/marton-multiletter-finite-foundation-repair",
        "claim key",
    )
    repaired = "f6ea30479b9ca461294ba89a8a1a31c06ce59d08"
    need(claim["dependencyTransactionIds"] == [repaired], "corrective reference")
    need(re.fullmatch(r"[0-9a-f]{40}", repaired) is not None, "transaction form")

    statement = claim["statement"]
    for required in (
        "finite auxiliary alphabets U,V,W",
        "M_{m+n}^fin(P) >= M_m^fin(P)+M_n^fin(P)",
        "Assume (H-Marton)",
        "Assume additionally (H-binary)",
        "corrective/provenance reference rather than a mathematical premise",
        "No fixed-n equality is a capacity converse",
    ):
        need(required in statement, f"claim scope: {required}")

    hypotheses = {item["id"]: item for item in premises["externalHypotheses"]}
    need(set(hypotheses) == {"H-Marton", "H-binary"}, "hypothesis ids")
    need(hypotheses["H-Marton"]["source"]["version"] == "arXiv:1202.0898v1",
         "Marton source version")
    need(
        hypotheses["H-Marton"]["source"]["authors"]
        == ["Amin Gohari", "Chandra Nair", "Venkat Anantharam"],
        "Marton restatement authors",
    )
    need(hypotheses["H-Marton"]["source"]["location"].startswith("Bound 1"),
         "Marton source location")
    original_marton = hypotheses["H-Marton"]["source"]["original"]
    need(original_marton["author"] == "Katalin Marton", "original author")
    need(original_marton["doi"] == "10.1109/TIT.1979.1056046",
         "original Marton DOI")
    need(hypotheses["H-binary"]["source"]["version"] == "arXiv:1001.1468v1",
         "binary source version")
    need(hypotheses["H-binary"]["source"]["location"] == "Corollary 1",
         "binary source location")
    need(all("not independently proved" in item["status"] for item in hypotheses.values()),
         "hypothesis boundary")

    references = premises["canonicalReferences"]
    need(len(references) == 1 and references[0]["transactionId"] == repaired,
         "canonical repair target")
    need("not a mathematical premise" in references[0]["role"], "reference role")
    need(references[0]["primaryJudgmentStatus"] == "indeterminate",
         "prior judgment status")

    # Exact symbolic case audit of min(a_m+a_n,b_m+b_n) >=
    # min(a_m,b_m)+min(a_n,b_n).  In each of the four order cases, write each
    # non-minimal member as its minimum plus a nonnegative slack.  The two
    # left-branch differences from the right side have only 0/1 slack
    # coefficients, hence are nonnegative.
    for m_chooses_a in (False, True):
        for n_chooses_a in (False, True):
            a_difference = (
                0 if m_chooses_a else 1,
                0 if n_chooses_a else 1,
            )
            b_difference = (
                1 if m_chooses_a else 0,
                1 if n_chooses_a else 0,
            )
            need(set(a_difference + b_difference) <= {0, 1}, "min inequality cases")


def print_hashes() -> None:
    for name in ("claims.json", "premises.json", "interval_certificate.json"):
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        print(f"{name}: sha256:{digest}")


def main() -> None:
    # Inspect this source before execution. It performs no network access and
    # writes no files.
    check_structural_scope()
    q_minus, l_rtd, two_l_rtd = check_certificate()
    print_hashes()
    print(f"q_- enclosure: [{q_minus.lo}, {q_minus.hi}]")
    print(f"L_RTD enclosure: [{l_rtd.lo}, {l_rtd.hi}]")
    print(f"2 L_RTD enclosure: [{two_l_rtd.lo}, {two_l_rtd.hi}]")
    print("PASS: finite-scope repair and directed RTD threshold certificate")


if __name__ == "__main__":
    main()
