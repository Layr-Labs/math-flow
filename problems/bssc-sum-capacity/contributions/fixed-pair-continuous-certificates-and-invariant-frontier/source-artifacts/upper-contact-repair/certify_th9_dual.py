#!/usr/bin/env python3
"""Attempt 017: interval certificate for a continuous full-Theorem-9 dual
upper bound at the fixed eq.-(16)-optimal auxiliary channel.

WHAT IS CERTIFIED.  For the exact-decimal channel pair

    G = (a, b) = (0.2068684034, 0.8268635311)   (P(G=0|X=0), P(G=0|X=1))
    K = (1-b, 1-a)                              (input/output reflection)

and the exact-decimal dual weights (a frozen one-parameter dual family at
EPS = 0.000172556)

    lambda[(19e)+2nd min branch] = lambda[(19i)+2nd min branch] = EPS
    lambda[(19l), I(Wa;Y) min path] = lambda[final a-side, right-left] = EPS
    lambda[(19m)] = 1/2 - EPS/2,   lambda[(19o)] = 1/2 - 3 EPS/2,

this script certifies, by outward-rounded interval arithmetic, a continuous
weak-duality upper bound U on the Theorem 9 (GK-Bound, full version,
January 2026 manuscript) sum-rate value at this channel, hence on C_sum of
BSSC(1/2).  The chain (derived in FULL.md):

  R1+R2 <= sum_i lambda_i * (row_i RHS)                    [Theorem 9 rows]
         = sum_ch c_ch I_ch(q0) + sum_{g in A,B,C}
             ( E_mu[f_W^g] + E_nuU[f_U^g] + E_nuV[f_V^g] ) [posterior ids]
        <= sum_ch c_ch I_ch(q0) + sum_g (alpha_g + beta_g q0)   [(D1),(D2)]
         = B(q0) <= B(1/2) = U                     [beta_tot = 0, concavity]

where the dual-feasibility conditions certified here are

  (D1)  every inner affine majorant used dominates its curve on ALL of [0,1]:
          group A: the tangent T_w of h = I_G - I_Y at each w in [0, T_A]
                   and the fixed tangent T_{T_A}   (analytic lemma: exact
                   h''-sign control + one thin check phi(T_A) > 0);
          group C: mirror statements for h_C = I_K - I_Z;
          group B: chord lines with exact 1e-33 intercepts,
                   ell_V >= f_V^B and ell_U >= f_U^B on [0,1]
                   (interval bisection plus two-sided contact guards);
  (D2)  for every w in [0,1], alpha_g + beta_g w >= f_W^g(w) + (inner
        majorant value at w), certified per group on a region decomposition
        (interval bisection + convex tangent bounds + concave endpoint
        bounds; near-tangency points receive backed-off interval checks).

The maximum over the input prior q0 is closed analytically: the certified
combination has c_Y = c_Z = (1+EPS)/2 >= 0, c_G = c_K = 0 and
beta_A + beta_B + beta_C = 0 EXACTLY (Phase-0 rational checks), so B(q0) is
concave and symmetric under q0 <-> 1-q0 and is maximized at q0 = 1/2.

The group-A/C outer lines retain a `BACKOFF = 1e-18`.  The group-B lines use a
`GROUP_B_BACKOFF = 1e-33`; directed monotonicity, complete two-sided contact
guards, and adaptive exterior segments certify their claimed nonnegativity.

Rounding model: interval_arithmetic.py provides 80-digit Decimal endpoints,
directed rounding, and Decimal.ln (documented correctly rounded) expanded one
representable number outward.  Python standard library only.

Run:  python3 certify_th9_dual.py [--audit-ambient-context]
"""

from __future__ import annotations

import argparse
import time
from decimal import (
    Decimal,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_UP,
    getcontext,
    localcontext,
    setcontext,
)
from fractions import Fraction

from interval_arithmetic import (
    D,
    HALF,
    IV,
    LN2,
    NEAREST,
    ONE,
    REPORTED_COMPARISON,
    ZERO,
    down_sub,
    up_add,
    up_mul,
    up_sub,
)

# ----------------------------------------------------------------------
# frozen exact decimals
#
# Fixed reflected binary pair and frozen line constants.  A high-precision
# numerical solve located the constants, but validity does not depend on that
# generator: every inequality is re-certified below from the exact decimals.
# ----------------------------------------------------------------------

A_CH = D("0.2068684034")
B_CH = D("0.8268635311")

EPS = D("0.000172556")
HALF_EPS = D("0.000086278")            # EPS/2, exact
THREE_HALF_EPS = D("0.000258834")      # 3*EPS/2, exact
W_19M = D("0.499913722")               # 1/2 - EPS/2, exact
W_19O = D("0.499741166")               # 1/2 - 3*EPS/2, exact
C1 = D("0.499913722")                  # (1-EPS)/2, exact
C1P = D("0.500086278")                 # (1+EPS)/2, exact

BACKOFF = D("1e-18")

# group A (and mirrored group C) certificate constants
T_A = D("0.223552668538408774737672966080")    # trunc of s*; phi(T_A) > 0
M_A0 = D("0.114285343005993681661925002371")   # near outer left contact
M_A1 = D("0.768455543733403745703862116196")   # near outer right contact
BETA_A = D("0.0455746969473466097687930352226")            # nearest-30
ALPHA_A = D("0.00484636345006208271335829634629")  # +1e-18 backoff, up-30
CI_A = D("0.606140352457671436157307542343")   # <= ci = root of h''
BETA_C = BETA_A.copy_negate()

# group B certificate constants
M_BV = D("0.770454053982572010542858483762")   # near f_V chord tangency
SLOPE_V = D("0.0026976853408719163997223206507487")  # limiting chord, down-34
# The exact zero-intercept limiting chord misses the true curve by about
# 4.9e-35 at the rounded contact above.  A 1e-33 intercept is still fifteen
# orders of magnitude smaller than the canonical 1e-18 backoff, while leaving
# a directed positive margin that can be covered on a genuine neighborhood.
GROUP_B_BACKOFF = D("1e-33")
ICPT_V = GROUP_B_BACKOFF
SLOPE_U = SLOPE_V.copy_negate()

# Derived constants must be computed under the 80-digit context: the sums
# below are exact there but would be silently rounded by the 28-digit
# default ambient context.
with localcontext(NEAREST):
    K0_CH = D(1) - B_CH        # 0.1731364689, exact
    K1_CH = D(1) - A_CH        # 0.7931315966, exact
    T_C = D(1) - T_A           # exact complements of the A constants
    M_C0 = D(1) - M_A1
    M_C1 = D(1) - M_A0
    ALPHA_C = ALPHA_A + BETA_A     # exact (<= 32 digits)
    M_BU = D(1) - M_BV
    ICPT_U = ICPT_V + SLOPE_V      # exact; ell_U(w) = ell_V(1-w)

DELTA_WIN = D("0.0625")        # tangent-bound window half-width
CONTACT_GUARD = D("1e-16")     # symmetric contact guard offset
ENDPOINT_MONO = D("0.01")      # exact-endpoint monotonicity neighborhood

# Validation landmarks, not inputs to dual feasibility
PREVIOUS_COMPARISON = D("0.369297196647212180877")
SAMPLED_CROSSCHECK = D("0.36929694657")
BASELINE_REPORTED = REPORTED_COMPARISON     # D("0.369296340638082")

MAX_CELLS = 500_000
MAX_DEPTH = 110
MIN_WIDTH = D("1e-40")

# ----------------------------------------------------------------------
# phase 0: exact rational audit of the dual combination
# ----------------------------------------------------------------------

YCH, ZCH, GCH, KCH = range(4)
GA, GB, GC = range(3)
CONST, WL, UL, VL = range(4)

KIND_MAP = {
    "W": ((CONST, 1), (WL, -1)),
    "U|W": ((WL, 1), (UL, -1)),
    "V|W": ((WL, 1), (VL, -1)),
    "UW": ((CONST, 1), (UL, -1)),
    "VW": ((CONST, 1), (VL, -1)),
    "X|UW": ((UL, 1),),
    "X|VW": ((VL, 1),),
}

# The six Theorem 9 rows used by the dual family, transcribed term by term
# from the manuscript display (19c)-(19p) and its final side conditions.
ROWS = {
    # (19e)-(19f) with the min replaced by its SECOND branch:
    # R1 <= I(Wc;Z)+I(Ua;Y|Wa)+I(Wa;G)-I(Wb;G)+I(Wb;K)-I(Wc;K)
    #       + I(Ub,Wb;G)-I(Ua,Wa;G)
    "r1_c_1": (1, 0, (
        (GC, "W", ZCH, 1), (GA, "U|W", YCH, 1),
        (GA, "W", GCH, 1), (GB, "W", GCH, -1),
        (GB, "W", KCH, 1), (GC, "W", KCH, -1),
        (GB, "UW", GCH, 1), (GA, "UW", GCH, -1),
    )),
    # (19i)-(19j) with the min replaced by its SECOND branch:
    # R2 <= I(Wc;Z)+I(Vc;Z|Wc) + I(Vb,Wb;K)-I(Vc,Wc;K)
    "r2_c_1": (0, 1, (
        (GC, "W", ZCH, 1), (GC, "V|W", ZCH, 1),
        (GB, "VW", KCH, 1), (GC, "VW", KCH, -1),
    )),
    # (19l), first (I(Wa;Y)) min path:
    # R1+R2 <= I(Wa;Y)+I(Wc;K)-I(Wb;K)+I(Wb;G)-I(Wa;G)
    #          + I(Va,Wa;G)-I(Vb,Wb;G)+I(Vb,Wb;K)-I(Vc,Wc;K)
    #          + I(Vc;Z|Wc)+I(X;Y|Va,Wa)
    "19l_a": (1, 1, (
        (GA, "W", YCH, 1),
        (GC, "W", KCH, 1), (GB, "W", KCH, -1),
        (GB, "W", GCH, 1), (GA, "W", GCH, -1),
        (GA, "VW", GCH, 1), (GB, "VW", GCH, -1),
        (GB, "VW", KCH, 1), (GC, "VW", KCH, -1),
        (GC, "V|W", ZCH, 1), (GA, "X|VW", YCH, 1),
    )),
    # (19m): R1+R2 <= I(Wa;Y)+I(Ua;Y|Wa)+I(Vc;Z|Wc)
    #                 + I(Ub,Wb;G)-I(Ua,Wa;G)-I(Vc;K|Wc)+I(X;K|Ub,Wb)
    "19m": (1, 1, (
        (GA, "W", YCH, 1), (GA, "U|W", YCH, 1), (GC, "V|W", ZCH, 1),
        (GB, "UW", GCH, 1), (GA, "UW", GCH, -1),
        (GC, "V|W", KCH, -1), (GB, "X|UW", KCH, 1),
    )),
    # (19o): R1+R2 <= I(Wc;Z)+I(Ua;Y|Wa)+I(Vc;Z|Wc)
    #                 + I(Vb,Wb;K)-I(Vc,Wc;K)-I(Ua;G|Wa)+I(X;G|Vb,Wb)
    "19o": (1, 1, (
        (GC, "W", ZCH, 1), (GA, "U|W", YCH, 1), (GC, "V|W", ZCH, 1),
        (GB, "VW", KCH, 1), (GC, "VW", KCH, -1),
        (GA, "U|W", GCH, -1), (GB, "X|VW", GCH, 1),
    )),
    # final a-side condition, right minus left:
    # 0 <= I(Ua;Y|Wa)-I(Ua;G|Wa) - I(X;Y|Va,Wa)+I(X;G|Va,Wa)
    "final_a_rml": (0, 0, (
        (GA, "U|W", YCH, 1), (GA, "U|W", GCH, -1),
        (GA, "X|VW", YCH, -1), (GA, "X|VW", GCH, 1),
    )),
}

WEIGHTS = {
    "r1_c_1": EPS, "r2_c_1": EPS, "19l_a": EPS, "final_a_rml": EPS,
    "19m": W_19M, "19o": W_19O,
}


def phase0_exact_audit() -> None:
    e = Fraction(EPS)
    half = Fraction(1, 2)
    # weight bookkeeping
    if not (Fraction(W_19M) == half - e / 2
            and Fraction(W_19O) == half - 3 * e / 2
            and Fraction(HALF_EPS) == e / 2
            and Fraction(THREE_HALF_EPS) == 3 * e / 2
            and Fraction(C1) == half - e / 2
            and Fraction(C1P) == half + e / 2):
        raise AssertionError("frozen weight decimals are not exact")
    if not (0 < e < Fraction(1, 3)):
        raise AssertionError("EPS out of the valid range")
    for weight in WEIGHTS.values():
        if not Fraction(weight) >= 0:
            raise AssertionError("negative dual weight")
    r1_sum = sum(Fraction(WEIGHTS[k]) * ROWS[k][0] for k in ROWS)
    r2_sum = sum(Fraction(WEIGHTS[k]) * ROWS[k][1] for k in ROWS)
    if not (r1_sum == 1 and r2_sum == 1):
        raise AssertionError("rate coefficients do not sum to one")

    # combined tensor, exactly
    tensor = [[[Fraction(0)] * 4 for _ in range(4)] for _ in range(3)]
    for key, (unused_r1, unused_r2, terms) in ROWS.items():
        w = Fraction(WEIGHTS[key])
        for group, kind, channel, sign in terms:
            for level, coeff in KIND_MAP[kind]:
                tensor[group][level][channel] += w * sign * coeff

    c1, c1p = half - e / 2, half + e / 2
    expected = [[[Fraction(0)] * 4 for _ in range(4)] for _ in range(3)]
    expected[GA][CONST][YCH] = c1p
    expected[GA][CONST][GCH] = -c1
    expected[GA][WL][YCH] = c1
    expected[GA][WL][GCH] = -c1
    expected[GA][UL][YCH] = Fraction(-1)
    expected[GA][UL][GCH] = Fraction(1)
    expected[GB][CONST][GCH] = c1
    expected[GB][CONST][KCH] = c1p
    expected[GB][UL][GCH] = -c1p
    expected[GB][UL][KCH] = c1
    expected[GB][VL][GCH] = c1
    expected[GB][VL][KCH] = -c1p
    expected[GC][CONST][ZCH] = c1p
    expected[GC][CONST][KCH] = -c1p
    expected[GC][WL][ZCH] = c1
    expected[GC][WL][KCH] = -c1
    expected[GC][VL][ZCH] = Fraction(-1)
    expected[GC][VL][KCH] = Fraction(1)
    if tensor != expected:
        raise AssertionError("combined tensor differs from the closed form")
    for ch, target in ((YCH, c1p), (ZCH, c1p), (GCH, 0), (KCH, 0)):
        if sum(tensor[g][CONST][ch] for g in range(3)) != target:
            raise AssertionError("constant-coefficient identity failed")

    # line bookkeeping for the q0-lemma: total slope must vanish exactly
    if not (Fraction(BETA_A) + Fraction(BETA_C) == 0
            and Fraction(SLOPE_V) + Fraction(SLOPE_U) == 0
            and Fraction(ALPHA_C) == Fraction(ALPHA_A) + Fraction(BETA_A)
            and Fraction(ICPT_U) == Fraction(ICPT_V) + Fraction(SLOPE_V)
            and Fraction(T_C) == 1 - Fraction(T_A)
            and Fraction(M_C0) == 1 - Fraction(M_A1)
            and Fraction(M_C1) == 1 - Fraction(M_A0)
            and Fraction(M_BU) == 1 - Fraction(M_BV)):
        raise AssertionError("mirror/line identities failed")

    # region orderings
    dw = Fraction(DELTA_WIN)
    fa0, fa1, fta, fci = (Fraction(M_A0), Fraction(M_A1), Fraction(T_A),
                          Fraction(CI_A))
    fbv = Fraction(M_BV)
    orderings = (
        0 < fa0 < fta < fci < fa1 - dw,
        fa1 + dw < 1,
        fa0 < half < fa1,
        0 < fbv - dw and fbv + dw < 1,
        Fraction(M_BU) - dw > 0,
        0 < half < fbv,
        1 - fbv < half < 1,
    )
    if not all(orderings):
        raise AssertionError("region ordering failed")

    # exact sign control of h'' (and, by mirror, h_C''):
    # ln(2) (m_G(1-m_G))(1-q^2) h''(q) has the sign of
    #   SGN(q) = a(1-a) - delta^2 + delta(1-2a) q,   affine increasing.
    fa, fb = Fraction(A_CH), Fraction(B_CH)
    delta = fb - fa
    sgn = lambda w: fa * (1 - fa) - delta * delta + delta * (1 - 2 * fa) * w  # noqa: E731
    if not delta * (1 - 2 * fa) > 0:
        raise AssertionError("SGN is not increasing")
    checks = (
        sgn(fta) < 0,          # h'' < 0 on [0, T_A]  (region A1 convex gap)
        sgn(fci) < 0,          # h'' < 0 on [T_A, CI_A]  (A2a concave gap)
        sgn(fa1 - dw) > 0,     # h'' > 0 on the A2c window (convex gap)
        # mirrors: h_C''(w) = h''(1-w) exactly
    )
    if not all(checks):
        raise AssertionError("h'' sign control failed")

    # group B window convexity: gap'' > 0 on the window iff the rational
    # quadratic R(w) > 0 there (V window; the U window uses R(1-w)).
    fk0 = Fraction(K0_CH)

    def mg_var(w):
        m = fa + w * delta
        return m * (1 - m)

    def mk_var(w):
        m = fk0 + w * delta
        return m * (1 - m)

    def r_quad(w):
        return c1 * mk_var(w) - c1p * mg_var(w)

    def quad_positive_on(lo, hi, f):
        # f is a rational quadratic q0 + q1 w + q2 w^2; positivity on
        # [lo, hi] from endpoint values plus the vertex (exact arithmetic):
        #   q2 = 2 (f(0) + f(1) - 2 f(1/2)),  q1 = (f(1) - f(-1)) / 2.
        vals = [f(lo), f(hi)]
        lead = 2 * (f(Fraction(0)) + f(Fraction(1))
                    - 2 * f(Fraction(1, 2)))
        if lead != 0:
            vertex = -(f(Fraction(1)) - f(Fraction(-1))) / (4 * lead)
            if lo < vertex < hi:
                vals.append(f(vertex))
        return all(v > 0 for v in vals)

    if not quad_positive_on(fbv - dw, fbv + dw, r_quad):
        raise AssertionError("group B V-window convexity failed")
    if not quad_positive_on(1 - fbv - dw, 1 - fbv + dw,
                            lambda w: r_quad(1 - w)):
        raise AssertionError("group B U-window convexity failed")

    print("phase0_exact_audit: all rational checks passed")
    print("  weights >= 0, rate sums = 1, combined tensor == closed form,")
    print("  c_Y = c_Z = (1+EPS)/2, c_G = c_K = 0, total line slope = 0,")
    print("  region orderings, h''-sign control, B-window convexity: exact")


# ----------------------------------------------------------------------
# interval curve layer (h2 with endpoint handling; the four MI curves)
# ----------------------------------------------------------------------

QUARTER = D("0.25")
THREEQ = D("0.75")


def iv_h2(p: IV) -> IV:
    """Binary entropy enclosure valid on cells touching 0 or 1.

    On [0, hi] with hi <= 1/4, h2 is increasing, so the exact range is
    [h2(max(0,lo)), h2(hi)] and [0, h2(hi)] is a valid enclosure; mirror
    near 1.  Interior cells use the standard formula.
    """
    if p.lo == p.hi and (p.lo == 0 or p.lo == 1):
        return ZERO
    if p.lo > 0 and p.hi < 1:
        return -(p * p.ln() + (ONE - p) * (ONE - p).ln()) / LN2
    if p.lo <= 0:
        if p.hi > QUARTER:
            raise ValueError(f"cell touching 0 too wide for iv_h2: {p}")
        hi_val = iv_h2(IV.point(p.hi))
        return IV(D(0), hi_val.hi)
    if p.hi >= 1:
        if p.lo < THREEQ:
            raise ValueError(f"cell touching 1 too wide for iv_h2: {p}")
        lo_val = iv_h2(IV.point(p.lo))
        return IV(D(0), lo_val.hi)
    raise AssertionError("unreachable")


H2_HALF = iv_h2(IV.point(D("0.5")))
H2_A = iv_h2(IV.point(A_CH))
H2_B = iv_h2(IV.point(B_CH))
H2_K0 = iv_h2(IV.point(K0_CH))
H2_K1 = iv_h2(IV.point(K1_CH))


def iy(q: IV) -> IV:
    # I_Y(q) = h2((1-q)/2) - (1-q);  channel rows (1/2,1/2) and (0,1)
    return iv_h2((ONE - q) * HALF) - (ONE - q)


def iyp(q: IV) -> IV:
    m = (ONE - q) * HALF
    return -HALF * ((ONE - m) / m).ln() / LN2 + ONE


def iz(q: IV) -> IV:
    # I_Z(q) = h2(1 - q/2) - q  (= h2(q/2) - q)
    return iv_h2(ONE - q * HALF) - q


def izp(q: IV) -> IV:
    m = ONE - q * HALF
    # d/dq h2(m) = h2'(m) * (-1/2);  h2'(m) = ln((1-m)/m)/ln 2
    return -HALF * ((ONE - m) / m).ln() / LN2 - ONE


DELTA_CH = IV.point(B_CH) - IV.point(A_CH)


def ig(q: IV) -> IV:
    m = IV.point(A_CH) + q * DELTA_CH
    return iv_h2(m) - (ONE - q) * H2_A - q * H2_B


def igp(q: IV) -> IV:
    m = IV.point(A_CH) + q * DELTA_CH
    return DELTA_CH * ((ONE - m) / m).ln() / LN2 + H2_A - H2_B


def ik(q: IV) -> IV:
    m = IV.point(K0_CH) + q * DELTA_CH
    return iv_h2(m) - (ONE - q) * H2_K0 - q * H2_K1


def ikp(q: IV) -> IV:
    m = IV.point(K0_CH) + q * DELTA_CH
    return DELTA_CH * ((ONE - m) / m).ln() / LN2 + H2_K0 - H2_K1


def h_curve(q: IV) -> IV:
    return ig(q) - iy(q)


def hp_curve(q: IV) -> IV:
    return igp(q) - iyp(q)


def hc_curve(q: IV) -> IV:
    return ik(q) - iz(q)


def hcp_curve(q: IV) -> IV:
    return ikp(q) - izp(q)


def fv_b(q: IV) -> IV:
    return IV.point(C1) * ig(q) - IV.point(C1P) * ik(q)


def fvp_b(q: IV) -> IV:
    return IV.point(C1) * igp(q) - IV.point(C1P) * ikp(q)


def fu_b(q: IV) -> IV:
    return IV.point(C1) * ik(q) - IV.point(C1P) * ig(q)


def fup_b(q: IV) -> IV:
    return IV.point(C1) * ikp(q) - IV.point(C1P) * igp(q)


# ----------------------------------------------------------------------
# gap functions (one per certified inequality family)
# ----------------------------------------------------------------------


class Gaps:
    """All certified gap functions, built from the frozen decimals."""

    def __init__(self) -> None:
        ta = IV.point(T_A)
        self.h_ta = h_curve(ta)
        self.hp_ta = hp_curve(ta)
        tc = IV.point(T_C)
        self.hc_tc = hc_curve(tc)
        self.hcp_tc = hcp_curve(tc)
        self.alpha_a = IV.point(ALPHA_A)
        self.beta_a = IV.point(BETA_A)
        self.alpha_c = IV.point(ALPHA_C)
        self.beta_c = IV.point(BETA_C)
        self.c1 = IV.point(C1)
        self.c1p = IV.point(C1P)

    # ---- group A ----
    def line_a(self, w: IV) -> IV:
        return self.alpha_a + self.beta_a * w

    def tang_a(self, w: IV) -> IV:
        return self.h_ta + self.hp_ta * (w - IV.point(T_A))

    def gap_a1(self, w: IV) -> IV:
        # region [0, T_A]: inner majorant is the tangent at w itself
        return self.line_a(w) - self.c1p * h_curve(w)

    def gap_a1_p(self, w: IV) -> IV:
        return self.beta_a - self.c1p * hp_curve(w)

    def gap_a2(self, w: IV) -> IV:
        # region [T_A, 1]: inner majorant is the fixed tangent at T_A
        return self.line_a(w) + self.c1 * h_curve(w) - self.tang_a(w)

    def gap_a2_p(self, w: IV) -> IV:
        return self.beta_a + self.c1 * hp_curve(w) - self.hp_ta

    # ---- group C (mirror) ----
    def line_c(self, w: IV) -> IV:
        return self.alpha_c + self.beta_c * w

    def tang_c(self, w: IV) -> IV:
        return self.hc_tc + self.hcp_tc * (w - IV.point(T_C))

    def gap_c1(self, w: IV) -> IV:
        # region [T_C, 1]
        return self.line_c(w) - self.c1p * hc_curve(w)

    def gap_c1_p(self, w: IV) -> IV:
        return self.beta_c - self.c1p * hcp_curve(w)

    def gap_c2(self, w: IV) -> IV:
        # region [0, T_C]
        return self.line_c(w) + self.c1 * hc_curve(w) - self.tang_c(w)

    def gap_c2_p(self, w: IV) -> IV:
        return self.beta_c + self.c1 * hcp_curve(w) - self.hcp_tc

    # ---- group B ----
    def gap_bv(self, w: IV) -> IV:
        return IV.point(ICPT_V) + IV.point(SLOPE_V) * w - fv_b(w)

    def gap_bv_p(self, w: IV) -> IV:
        return IV.point(SLOPE_V) - fvp_b(w)

    def gap_bu(self, w: IV) -> IV:
        return IV.point(ICPT_U) + IV.point(SLOPE_U) * w - fu_b(w)

    def gap_bu_p(self, w: IV) -> IV:
        return IV.point(SLOPE_U) - fup_b(w)


# ----------------------------------------------------------------------
# certification helpers
# ----------------------------------------------------------------------


class SegmentStats:
    def __init__(self) -> None:
        self.cells = 0
        self.max_depth = 0
        self.centered = 0
        self.worst: Decimal | None = None

    def record(self, depth: int, margin: Decimal, centered: bool) -> None:
        self.cells += 1
        self.max_depth = max(self.max_depth, depth)
        self.centered += centered
        if self.worst is None or margin < self.worst:
            self.worst = margin


def iv_abs_hi(x: IV) -> Decimal:
    return max(x.lo.copy_abs(), x.hi.copy_abs())


def certify_positive_segment(name, func, func_p, lo, hi, stats,
                             deriv_ok_at_ends=False) -> None:
    """Prove func > 0 on [lo, hi] by adaptive bisection (plain value form,
    centered form fallback on cells where the derivative is regular)."""
    if lo == hi:
        return
    stack = [(lo, hi, 0)]
    while stack:
        if stats.cells > MAX_CELLS:
            raise AssertionError(f"{name}: cell budget exceeded")
        x, y, depth = stack.pop()
        if depth > MAX_DEPTH or up_sub(y, x) < MIN_WIDTH:
            raise AssertionError(
                f"{name}: not certifiably positive near [{x}, {y}] "
                f"(depth {depth}); possible dual-feasibility failure")
        cell = IV(x, y)
        value = func(cell)
        if value.lo > 0:
            stats.record(depth, value.lo, False)
            continue
        with localcontext(NEAREST):
            mid = (x + y) / D(2)
        if func_p is not None and (deriv_ok_at_ends or (x > 0 and y < 1)):
            at_mid = func(IV.point(mid))
            deriv = func_p(cell)
            halfwidth = up_mul(up_sub(y, x), D("0.5"))
            margin = down_sub(at_mid.lo, up_mul(iv_abs_hi(deriv), halfwidth))
            if margin > 0:
                stats.record(depth, margin, True)
                continue
        stack.append((x, mid, depth + 1))
        stack.append((mid, y, depth + 1))


def tangent_bound(name, func, func_p, m, radius) -> Decimal:
    """Convex-region bound: min over the region >= f(M).lo - |f'(M)|.hi * r.
    Caller must have certified convexity of func on the region."""
    g0 = func(IV.point(m))
    g1 = func_p(IV.point(m))
    penalty = up_mul(iv_abs_hi(g1), radius)
    floor = down_sub(g0.lo, penalty)
    if not (g0.lo > 0 and floor > 0):
        raise AssertionError(
            f"{name}: tangent bound failed: f(M)={g0}, |f'|<= "
            f"{iv_abs_hi(g1):.3E}, floor={floor}")
    print(f"  {name}: f(M) in [{g0.lo:.6E}, {g0.hi:.6E}], "
          f"|f'(M)| <= {iv_abs_hi(g1):.3E}, certified min >= {floor:.6E}")
    return floor


def endpoint_bound(name, func, lo, hi) -> Decimal:
    """Concave-region bound: min over [lo,hi] is at an endpoint.
    Caller must have certified concavity of func on the region."""
    va = func(IV.point(lo))
    vb = func(IV.point(hi))
    if not (va.lo > 0 and vb.lo > 0):
        raise AssertionError(f"{name}: endpoint bound failed: {va}, {vb}")
    floor = min(va.lo, vb.lo)
    print(f"  {name}: f({lo}) >= {va.lo:.6E}, f({hi}) >= {vb.lo:.6E} "
          f"(concave => min at endpoints)")
    return floor


def monotone_endpoint_bound(name, func, func_p, lo, hi, increasing) -> None:
    """Close an endpoint neighborhood by a directed derivative sign.

    The canonical certificate used exact-zero endpoint gaps.  This repaired
    certificate has a strictly positive 1e-33 group-B intercept, so accepting
    either a directed nonnegative endpoint enclosure or a strictly positive
    one keeps the check valid without pretending that equality is attained.
    """
    va = func(IV.point(lo))
    vb = func(IV.point(hi))
    deriv = func_p(IV(lo, hi))
    endpoint = va if increasing else vb
    if endpoint.lo < 0:
        raise AssertionError(f"{name}: endpoint is negative: {endpoint}")
    if increasing:
        if not (deriv.lo > 0 and vb.lo > 0):
            raise AssertionError(f"{name}: increasing endpoint closure failed")
    elif not (deriv.hi < 0 and va.lo > 0):
        raise AssertionError(f"{name}: decreasing endpoint closure failed")
    print(f"  {name}: nonnegative endpoint and directed monotonicity certified")


# ----------------------------------------------------------------------
# phases 1-6
# ----------------------------------------------------------------------


def phase1_inner_majorants(gaps: Gaps) -> None:
    """(D1) for groups A and C: the tangent majorant lemma.

    Lemma (group A).  Let ci be the unique root of h'' (exact sign control
    via SGN, Phase 0: h'' < 0 on [0, T_A] and on [T_A, CI_A] subset [0, ci),
    h'' > 0 right of the A2c window's left edge).  For w in [0, T_A], the
    tangent T_w(q) = h(w) + h'(w)(q - w) satisfies T_w >= h on [0, 1]:
      - on [0, ci]: h is concave there and w is in [0, ci], so the tangent
        dominates h on the whole concave stretch;
      - on [ci, 1]: h is convex, hence h <= chord from (ci, h(ci)) to
        (1, h(1)=0); T_w dominates the chord because T_w(ci) >= h(ci) and
        T_w(1) = phi(w) >= phi(T_A) > 0 = h(1), phi decreasing on [0, T_A]
        (phi' = (1-w) h'' < 0 there).
    The same argument with the certified thin value phi(T_A) > 0 covers the
    fixed tangent T_{T_A} used on [T_A, 1].  Mirror statement for group C
    with phi_C(w) = h_C(w) - w h_C'(w) and phi_C(T_C) = phi(1 - T_C) by the
    exact reflection identity h_C(q) = h(1-q).
    """
    phi_a = gaps.h_ta + (ONE - IV.point(T_A)) * gaps.hp_ta
    if not phi_a.lo > 0:
        raise AssertionError(f"phi(T_A) not certifiably positive: {phi_a}")
    phi_c = gaps.hc_tc - IV.point(T_C) * gaps.hcp_tc
    if not phi_c.lo > 0:
        raise AssertionError(f"phi_C(T_C) not certifiably positive: {phi_c}")
    print("phase1_inner_majorants:")
    print(f"  phi(T_A)  in [{phi_a.lo:.6E}, {phi_a.hi:.6E}]  > 0")
    print(f"  phi_C(T_C) in [{phi_c.lo:.6E}, {phi_c.hi:.6E}]  > 0")
    print("  with Phase-0 h''-sign control: every tangent T_w (w <= T_A),")
    print("  the fixed tangents at T_A / T_C, and their group-C mirrors")
    print("  dominate their curves on all of [0,1]  --  (D1) for A and C")


def phase2_value() -> IV:
    iy_half = iy(IV.point(HALF.lo))
    iz_half = iz(IV.point(HALF.lo))
    cyz = IV.point(C1P)
    line_a_half = IV.point(ALPHA_A) + IV.point(BETA_A) * HALF
    line_c_half = IV.point(ALPHA_C) + IV.point(BETA_C) * HALF
    line_b_half = (IV.point(ICPT_U) + IV.point(SLOPE_U) * HALF
                   + IV.point(ICPT_V) + IV.point(SLOPE_V) * HALF)
    value = (cyz * (iy_half + iz_half)
             + line_a_half + line_b_half + line_c_half)
    print("phase2_value:")
    print(f"  I_Y(1/2) in {iy_half}")
    print(f"  U = B(1/2) in {value}")
    print(f"  enclosure width {value.width():.3E}")
    margin_frontier = down_sub(PREVIOUS_COMPARISON, value.hi)
    margin_reported = down_sub(value.lo, BASELINE_REPORTED)
    if not value.hi < PREVIOUS_COMPARISON:
        raise AssertionError("U does not improve the stored comparison")
    if not value.lo > BASELINE_REPORTED:
        # a failure here would mean MOVED territory; report loudly instead
        raise AssertionError(
            "U is below the reported decimal; re-audit before claiming MOVED")
    print(f"  U.hi - comparison 0.369297196647212180877 = "
          f"-{margin_frontier}")
    print(f"  U.lo - reported 0.369296340638082          = +{margin_reported}")
    print(f"  U.hi - sampled cross-check ~0.36929694657 = "
          f"{str(up_sub(value.hi, SAMPLED_CROSSCHECK))}")
    return value


def phase3_tangent_and_endpoint(gaps: Gaps) -> None:
    print("phase3_tangent_and_endpoint_bounds:")
    r_a1 = max(up_sub(T_A, M_A0), M_A0)
    tangent_bound("A1  [0,T_A] @M_A0     ", gaps.gap_a1, gaps.gap_a1_p,
                  M_A0, r_a1)
    endpoint_bound("A2a [T_A,CI_A]        ", gaps.gap_a2, T_A, CI_A)
    tangent_bound("A2c window @M_A1      ", gaps.gap_a2, gaps.gap_a2_p,
                  M_A1, DELTA_WIN)
    r_c1 = max(up_sub(M_C1, T_C), up_sub(D(1), M_C1))
    tangent_bound("C1  [T_C,1] @M_C1     ", gaps.gap_c1, gaps.gap_c1_p,
                  M_C1, r_c1)
    endpoint_bound("C2a [1-CI_A,T_C]      ", gaps.gap_c2,
                   down_sub(D(1), CI_A), T_C)
    tangent_bound("C2c window @M_C0      ", gaps.gap_c2, gaps.gap_c2_p,
                  M_C0, DELTA_WIN)
    monotone_endpoint_bound("BV  endpoint [0,0.01]      ", gaps.gap_bv,
                            gaps.gap_bv_p, D(0), ENDPOINT_MONO, True)
    monotone_endpoint_bound("BU  endpoint [0.99,1]      ", gaps.gap_bu,
                            gaps.gap_bu_p,
                            down_sub(D(1), ENDPOINT_MONO), D(1), False)
    tangent_bound("BV  guard around M_BV ", gaps.gap_bv, gaps.gap_bv_p,
                  M_BV, CONTACT_GUARD)
    tangent_bound("BU  guard around M_BU ", gaps.gap_bu, gaps.gap_bu_p,
                  M_BU, CONTACT_GUARD)


def phase4_bisection(gaps: Gaps) -> int:
    print("phase4_bisection_segments:")
    total = 0
    segments = (
        # group A: gap_a2 on [CI_A, M_A1-D] and [M_A1+D, 1]
        ("A2b", gaps.gap_a2, gaps.gap_a2_p, CI_A, down_sub(M_A1, DELTA_WIN),
         False),
        ("A2d", gaps.gap_a2, gaps.gap_a2_p, up_add(M_A1, DELTA_WIN), D(1),
         False),
        # group C: gap_c2 on [0, M_C0-D] and [M_C0+D, 1-CI_A]
        ("C2d", gaps.gap_c2, gaps.gap_c2_p, D(0), down_sub(M_C0, DELTA_WIN),
         False),
        ("C2b", gaps.gap_c2, gaps.gap_c2_p, up_add(M_C0, DELTA_WIN),
         down_sub(D(1), CI_A), False),
        # group B: chord-line gaps outside the windows (derivatives are
        # regular on all of [0,1]: only channels G, K are involved)
        ("BV-left ", gaps.gap_bv, gaps.gap_bv_p, ENDPOINT_MONO,
         down_sub(M_BV, CONTACT_GUARD), True),
        ("BV-right", gaps.gap_bv, gaps.gap_bv_p,
         up_add(M_BV, CONTACT_GUARD),
         D(1), True),
        ("BU-left ", gaps.gap_bu, gaps.gap_bu_p, D(0),
         down_sub(M_BU, CONTACT_GUARD), True),
        ("BU-right", gaps.gap_bu, gaps.gap_bu_p,
         up_add(M_BU, CONTACT_GUARD),
         down_sub(D(1), ENDPOINT_MONO), True),
    )
    for name, func, func_p, lo, hi, deriv_ok in segments:
        stats = SegmentStats()
        t0 = time.time()
        certify_positive_segment(name, func, func_p, lo, hi, stats, deriv_ok)
        total += stats.cells
        print(f"  {name} [{str(lo)[:12]}, {str(hi)[:12]}]: "
              f"cells={stats.cells}, max depth={stats.max_depth}, "
              f"centered={stats.centered}, "
              f"worst margin={stats.worst:.6E} [{time.time()-t0:.1f}s]")
    return total


def run_certificate() -> dict:
    gaps = Gaps()
    phase0_exact_audit()
    phase1_inner_majorants(gaps)
    value = phase2_value()
    phase3_tangent_and_endpoint(gaps)
    cells = phase4_bisection(gaps)
    print()
    print("CERTIFIED: continuous dual feasibility (D1)+(D2) on [0,1] for all")
    print("three auxiliary groups, hence for every input prior q0 and every")
    print("Theorem 9 auxiliary structure at the fixed channel pair:")
    print(f"  C_sum(BSSC 1/2) <= U,  U in {value}")
    print(f"  headline decimal: U <= {value.hi}")
    return {"value": value, "cells": cells}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-ambient-context", action="store_true",
                        help="re-run under hostile process-wide contexts")
    args = parser.parse_args()
    t0 = time.time()
    result = run_certificate()
    print(f"total time {time.time()-t0:.1f}s")
    if args.audit_ambient_context:
        reference = result["value"]
        saved = getcontext().copy()
        try:
            for precision, rounding in ((5, ROUND_UP), (7, ROUND_FLOOR),
                                        (3, ROUND_CEILING)):
                getcontext().prec = precision
                getcontext().rounding = rounding
                hostile = run_certificate()
                if hostile["value"] != reference:
                    raise AssertionError(
                        f"ambient Decimal context leaked at {precision=}, "
                        f"{rounding=}")
        finally:
            setcontext(saved)
        print("ambient_context_audit: passed "
              "(3 hostile contexts, identical certified value)")


if __name__ == "__main__":
    main()
