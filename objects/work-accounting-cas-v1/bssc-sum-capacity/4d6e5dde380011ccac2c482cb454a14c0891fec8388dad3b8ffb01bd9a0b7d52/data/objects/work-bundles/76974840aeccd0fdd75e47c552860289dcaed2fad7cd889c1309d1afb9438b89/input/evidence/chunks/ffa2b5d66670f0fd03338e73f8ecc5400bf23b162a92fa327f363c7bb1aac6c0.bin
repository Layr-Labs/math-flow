#!/usr/bin/env python3
"""Independent hostile-case audit for the ported UV identities.

This is corroboration of the analytic proof, not a finite-alphabet proof by
testing.  It deliberately includes zero-probability and deterministic channel
rows that are absent from the source randomized audit.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import runpy
from pathlib import Path
import sys


TOL = 3.0e-11


def load_source_audit():
    sys.dont_write_bytecode = True
    source = (
        Path(__file__).parent
        / "source-artifacts"
        / "upper-uv-additivity"
        / "verify_uv_factorization.py"
    )
    return runpy.run_path(str(source), run_name="uv_source_audit")


def hostile_channels():
    constant = [
        [[1.0, 0.0], [0.0, 0.0]],
        [[1.0, 0.0], [0.0, 0.0]],
    ]
    identity_antidentity = [
        [[0.0, 1.0], [0.0, 0.0]],
        [[0.0, 0.0], [1.0, 0.0]],
    ]
    bssc_common_noise = [
        [[0.5, 0.0], [0.5, 0.0]],
        [[0.0, 0.0], [0.5, 0.5]],
    ]
    return [constant, identity_antidentity, bssc_common_noise]


def hostile_inputs():
    laws = []
    laws.append({(0, 0, 0): 0.5, (0, 1, 1): 0.5})
    laws.append(
        {
            (x1 ^ x2, x1, x2): 0.25
            for x1 in range(2)
            for x2 in range(2)
        }
    )
    laws.append({(1, 1, 0): 1.0})
    laws.append(
        {
            (x1, x1, x2): probability
            for (x1, x2), probability in {
                (0, 0): 0.1,
                (0, 1): 0.2,
                (1, 0): 0.3,
                (1, 1): 0.4,
            }.items()
        }
    )
    return laws


def audit_hostile_chain_identities(api):
    cmi = api["conditional_mi"]
    product_joint = api["product_joint"]
    worst = Decimal(0)
    minimum_slack = float("inf")
    a, x1, x2, y1, z1, y2, z2 = range(7)

    count = 0
    for w1 in hostile_channels():
        for w2 in hostile_channels():
            for p_ax in hostile_inputs():
                count += 1
                joint = product_joint(p_ax, w1, w2)
                cross_1 = cmi(joint, (y1,), (z2,), (x1, a))
                cross_2 = cmi(joint, (z2,), (y1,), (x2, a))
                iy12 = cmi(joint, (x1, x2), (y1, y2), (a,))
                iz12 = cmi(joint, (x1, x2), (z1, z2), (a,))
                iy1 = cmi(joint, (x1,), (y1,), (a, z2))
                iz1 = cmi(joint, (x1,), (z1,), (a, z2))
                iy2 = cmi(joint, (x2,), (y2,), (a, y1))
                iz2 = cmi(joint, (x2,), (z2,), (a, y1))
                cross = cmi(joint, (y1,), (z2,), (a,))

                residuals = [cross_1, cross_2]
                residuals.append((iy12 - iz12) - (iy1 - iz1 + iy2 - iz2))
                for lam in (0.0, 1.0, 1.7, 3.0):
                    rhs = iy1 - lam * iz1 + iy2 - lam * iz2
                    rhs -= (lam - 1.0) * cross
                    residuals.append(iy12 - lam * iz12 - rhs)
                for residual in residuals:
                    worst = max(worst, Decimal(str(abs(residual))))

                iy_plain = cmi(joint, (x1, x2), (y1, y2))
                iy_parts = cmi(joint, (x1,), (y1,)) + cmi(
                    joint, (x2,), (y2,)
                )
                iz_plain = cmi(joint, (x1, x2), (z1, z2))
                iz_parts = cmi(joint, (x1,), (z1,)) + cmi(
                    joint, (x2,), (z2,)
                )
                minimum_slack = min(
                    minimum_slack, iy_parts - iy_plain, iz_parts - iz_plain
                )

    assert worst < Decimal(str(TOL)), worst
    assert minimum_slack > -TOL, minimum_slack
    return count, worst, minimum_slack


def h2(q: Decimal) -> Decimal:
    if q == 0 or q == 1:
        return Decimal(0)
    one = Decimal(1)
    return -(q * q.ln() + (one - q) * (one - q).ln()) / Decimal(2).ln()


def bssc_t(q: Decimal) -> Decimal:
    one = Decimal(1)
    iy = h2((one - q) / 2) - (one - q)
    iz = h2(q / 2) - q
    return iy - iz


def audit_bssc_specialization():
    getcontext().prec = 90
    one = Decimal(1)
    h = h2(one / 4)
    c = h - one / 2
    r = h - Decimal(3) / 4
    q = Decimal(4) / 5

    # Exact proof inputs: the canonical sharp support gives t(q) <= 2 r q.
    # The source contact mixture saturates that support at q=4/5 and has
    # barycenter 1/2 after adding mass 3/8 at q=0.
    contact_residual = bssc_t(q) - Decimal(8) * r / 5
    barycenter = Decimal(5) / 8 * q + Decimal(3) / 8 * Decimal(0)
    envelope_contact = Decimal(5) / 8 * bssc_t(q)
    uv_value = c + r
    closed_form = 2 * h - Decimal(5) / 4

    assert abs(contact_residual) < Decimal("1e-80"), contact_residual
    assert barycenter == one / 2, barycenter
    assert abs(envelope_contact - r) < Decimal("1e-80")
    assert abs(uv_value - closed_form) < Decimal("1e-88")

    y = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(0), Fraction(1)),
    )
    z = (
        (Fraction(1), Fraction(0)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    for x in range(2):
        for output in range(2):
            assert y[1 - x][output] == z[x][1 - output]
            assert z[1 - x][output] == y[x][1 - output]

    return contact_residual, uv_value


def main():
    api = load_source_audit()
    count, worst, slack = audit_hostile_chain_identities(api)
    contact, value = audit_bssc_specialization()
    print(f"hostile product laws checked: {count}")
    print(f"largest hostile identity residual: {worst:.3E}")
    print(f"minimum hostile MI-subadditivity slack: {slack:.3e}")
    print(f"BSSC contact residual (90-digit Decimal): {contact:.3E}")
    print(f"exact-form numerical value: {value}")
    print("PASS")


if __name__ == "__main__":
    main()
