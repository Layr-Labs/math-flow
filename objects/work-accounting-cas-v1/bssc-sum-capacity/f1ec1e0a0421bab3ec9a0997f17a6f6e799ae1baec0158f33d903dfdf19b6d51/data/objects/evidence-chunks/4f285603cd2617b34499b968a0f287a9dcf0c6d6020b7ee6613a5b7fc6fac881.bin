#!/usr/bin/env python3
"""Outward fixed-pair dual certificate under the declared theorem premise."""

from collections import defaultdict
from dataclasses import dataclass
from decimal import (Context, Decimal, ROUND_CEILING, ROUND_FLOOR,
                     ROUND_HALF_EVEN, ROUND_UP, getcontext, setcontext)
from fractions import Fraction

D = Decimal
NEAR = Context(prec=80, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=80, rounding=ROUND_FLOOR)
UP = Context(prec=80, rounding=ROUND_CEILING)


@dataclass(frozen=True)
class IV:
    lo: Decimal
    hi: Decimal

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError(self)

    @staticmethod
    def point(x):
        x = x if isinstance(x, Decimal) else D(x)
        return IV(x, x)

    def __add__(self, y):
        return IV(DOWN.add(self.lo, y.lo), UP.add(self.hi, y.hi))

    def __neg__(self):
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, y):
        return self + (-y)

    def __mul__(self, y):
        p = ((self.lo, y.lo), (self.lo, y.hi),
             (self.hi, y.lo), (self.hi, y.hi))
        return IV(min(DOWN.multiply(x, z) for x, z in p),
                  max(UP.multiply(x, z) for x, z in p))

    def __truediv__(self, y):
        if y.lo <= 0 <= y.hi:
            raise ZeroDivisionError(y)
        return self * IV(DOWN.divide(D(1), y.hi), UP.divide(D(1), y.lo))

    def ln(self):
        if self.lo <= 0:
            raise ValueError(self)
        lo, hi = NEAR.ln(self.lo), NEAR.ln(self.hi)
        return IV(lo.next_minus(context=NEAR), hi.next_plus(context=NEAR))

    def __str__(self):
        return f"[{self.lo}, {self.hi}]"


Q = IV.point
ZERO, ONE, HALF = Q(0), Q(1), Q("0.5")
LN2 = Q(2).ln()
HEADLINE = D("0.369296945969202842443")
EXPECTED_VALUE = IV(
    D("0.36929694596920284244271335135600317726937686320586339865039784778686683932875798"),
    D("0.36929694596920284244271335135600317726937686320586339865039784778686683932875818"),
)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def h2(p):
    if p.lo == p.hi and p.lo in (0, 1):
        return ZERO
    if p.lo > 0 and p.hi < 1:
        return -(p * p.ln() + (ONE - p) * (ONE - p).ln()) / LN2
    if p.lo <= 0 and p.hi <= D(".25"):
        return IV(D(0), h2(Q(p.hi)).hi)
    if p.hi >= 1 and p.lo >= D(".75"):
        return IV(D(0), h2(Q(p.lo)).hi)
    raise ValueError(p)


# Every numeral below is an exact decimal rational.
A_CH = D("0.206961624915382")
B_CH = D("0.826953249115544")
K0_CH = D("0.173046750884456")
K1_CH = D("0.793038375084618")
EPS = D("0.000173428163029")
C1 = D("0.4999132859184855")
C1P = D("0.5000867140815145")
W_M = D("0.4999132859184855")
W_O = D("0.4997398577554565")

TA = D("0.223554338099290337686997491745")
MA0 = D("0.114270117882180886477206425091")
MA1 = D("0.768484852026196875796918575693")
BA = D("0.0455668698298748564310479904957")
AA = D("0.00484278650837243101713855267415")
CI = D("0.606174265413707974748966890325")
MBV = D("0.770453933591712211652688419314")
SV = D("0.00271239427013419822092236108071")
IV0 = D("1e-18")
WIN = D("0.0625")
TC = NEAR.subtract(D(1), TA)
MC0 = NEAR.subtract(D(1), MA1)
MC1 = NEAR.subtract(D(1), MA0)
AC = NEAR.add(AA, BA)
MBU = NEAR.subtract(D(1), MBV)
IU0 = NEAR.add(IV0, SV)

H_A, H_B = h2(Q(A_CH)), h2(Q(B_CH))
H_K0, H_K1 = h2(Q(K0_CH)), h2(Q(K1_CH))
DQ = Q(B_CH) - Q(A_CH)


def iy(q):
    return h2((ONE - q) * HALF) - (ONE - q)


def iyp(q):
    m = (ONE - q) * HALF
    return -HALF * ((ONE - m) / m).ln() / LN2 + ONE


def iz(q):
    return h2(ONE - q * HALF) - q


def izp(q):
    m = ONE - q * HALF
    return -HALF * ((ONE - m) / m).ln() / LN2 - ONE


def ig(q):
    m = Q(A_CH) + q * DQ
    return h2(m) - (ONE - q) * H_A - q * H_B


def igp(q):
    m = Q(A_CH) + q * DQ
    return DQ * ((ONE - m) / m).ln() / LN2 + H_A - H_B


def ik(q):
    m = Q(K0_CH) + q * DQ
    return h2(m) - (ONE - q) * H_K0 - q * H_K1


def ikp(q):
    m = Q(K0_CH) + q * DQ
    return DQ * ((ONE - m) / m).ln() / LN2 + H_K0 - H_K1


def h(q): return ig(q) - iy(q)
def hp(q): return igp(q) - iyp(q)
def hc(q): return ik(q) - iz(q)
def hcp(q): return ikp(q) - izp(q)
def fv(q): return Q(C1) * ig(q) - Q(C1P) * ik(q)
def fvp(q): return Q(C1) * igp(q) - Q(C1P) * ikp(q)
def fu(q): return Q(C1) * ik(q) - Q(C1P) * ig(q)
def fup(q): return Q(C1) * ikp(q) - Q(C1P) * igp(q)


# Six premise-bound Theorem-9 rows from the declared foundation transaction.
# In order these are R1A(1), R2T(1), SR(1,C), SL(2,U), SR(2,U), and
# F_Y_right_minus_left.  A term is (group, MI-kind, channel, sign).
GA, GB, GC = range(3)
Y, Z, G, K = range(4)
CONST, WL, UL, VL = range(4)
KINDS = {
    "W": ((CONST, 1), (WL, -1)),
    "U|W": ((WL, 1), (UL, -1)),
    "V|W": ((WL, 1), (VL, -1)),
    "UW": ((CONST, 1), (UL, -1)),
    "VW": ((CONST, 1), (VL, -1)),
    "X|UW": ((UL, 1),), "X|VW": ((VL, 1),),
}
ROWS = (
    (1, 0, ((GC,"W",Z,1),(GA,"U|W",Y,1),(GA,"W",G,1),
            (GB,"W",G,-1),(GB,"W",K,1),(GC,"W",K,-1),
            (GB,"UW",G,1),(GA,"UW",G,-1))),
    (0, 1, ((GC,"W",Z,1),(GC,"V|W",Z,1),
            (GB,"VW",K,1),(GC,"VW",K,-1))),
    (1, 1, ((GA,"W",Y,1),(GC,"W",K,1),(GB,"W",K,-1),
            (GB,"W",G,1),(GA,"W",G,-1),(GA,"VW",G,1),
            (GB,"VW",G,-1),(GB,"VW",K,1),(GC,"VW",K,-1),
            (GC,"V|W",Z,1),(GA,"X|VW",Y,1))),
    (1, 1, ((GA,"W",Y,1),(GA,"U|W",Y,1),(GC,"V|W",Z,1),
            (GB,"UW",G,1),(GA,"UW",G,-1),(GC,"V|W",K,-1),
            (GB,"X|UW",K,1))),
    (1, 1, ((GC,"W",Z,1),(GA,"U|W",Y,1),(GC,"V|W",Z,1),
            (GB,"VW",K,1),(GC,"VW",K,-1),(GA,"U|W",G,-1),
            (GB,"X|VW",G,1))),
    (0, 0, ((GA,"U|W",Y,1),(GA,"U|W",G,-1),
            (GA,"X|VW",Y,-1),(GA,"X|VW",G,1))),
)
WEIGHTS = (EPS, EPS, EPS, W_M, W_O, EPS)


def exact_audit():
    e, half = Fraction(EPS), Fraction(1, 2)
    need(Fraction(K0_CH)==1-Fraction(B_CH) and
         Fraction(K1_CH)==1-Fraction(A_CH), "reflected channel")
    need(Fraction(C1) == half-e/2 and Fraction(C1P) == half+e/2 and
         Fraction(W_M) == half-e/2 and Fraction(W_O) == half-3*e/2,
         "weight identities")
    need(all(Fraction(w) >= 0 for w in WEIGHTS), "negative weight")
    need(sum(Fraction(w)*row[0] for w,row in zip(WEIGHTS,ROWS)) == 1 and
         sum(Fraction(w)*row[1] for w,row in zip(WEIGHTS,ROWS)) == 1,
         "rate coefficients")
    got = defaultdict(Fraction)
    for weight, (_, _, terms) in zip(WEIGHTS, ROWS):
        for group, kind, channel, sign in terms:
            for level, coefficient in KINDS[kind]:
                got[group,level,channel] += Fraction(weight)*sign*coefficient
    expected = {
        (GA,CONST,Y):half+e/2,(GA,CONST,G):-(half-e/2),
        (GA,WL,Y):half-e/2,(GA,WL,G):-(half-e/2),
        (GA,UL,Y):-1,(GA,UL,G):1,
        (GB,CONST,G):half-e/2,(GB,CONST,K):half+e/2,
        (GB,UL,G):-(half+e/2),(GB,UL,K):half-e/2,
        (GB,VL,G):half-e/2,(GB,VL,K):-(half+e/2),
        (GC,CONST,Z):half+e/2,(GC,CONST,K):-(half+e/2),
        (GC,WL,Z):half-e/2,(GC,WL,K):-(half-e/2),
        (GC,VL,Z):-1,(GC,VL,K):1,
    }
    need({k:v for k,v in got.items() if v} == expected, "combined tensor")
    for ch,target in ((Y,half+e/2),(Z,half+e/2),(G,0),(K,0)):
        need(sum(got[g,CONST,ch] for g in range(3)) == target,
             "constant/prior coefficients")
    need(Fraction(TC)==1-Fraction(TA) and Fraction(MC0)==1-Fraction(MA1)
         and Fraction(MC1)==1-Fraction(MA0) and
         Fraction(AC)==Fraction(AA)+Fraction(BA) and
         Fraction(MBU)==1-Fraction(MBV) and
         Fraction(IU0)==Fraction(IV0)+Fraction(SV), "mirror lines")

    dw, a, b = Fraction(WIN), Fraction(A_CH), Fraction(B_CH)
    ta, ma0, ma1, ci, mbv = map(Fraction, (TA,MA0,MA1,CI,MBV))
    need(0<ma0<ta<ci<ma1-dw and ma1+dw<1 and
         0<mbv-dw<mbv+dw<1 and 0<Fraction(MBU)-dw, "region order")
    delta = b-a
    sgn = lambda q: a*(1-a)-delta*delta+delta*(1-2*a)*q
    need(delta*(1-2*a)>0 and sgn(ta)<0 and sgn(ci)<0 and
         sgn(ma1-dw)>0, "curvature signs")

    k0, c1, c1p = Fraction(K0_CH), Fraction(C1), Fraction(C1P)
    def var(x0, q):
        m=x0+q*delta
        return m*(1-m)
    def rq(q): return c1*var(k0,q)-c1p*var(a,q)
    def positive_quadratic(lo, hi, f):
        values=[f(lo),f(hi)]
        lead=2*(f(Fraction(0))+f(Fraction(1))-2*f(Fraction(1,2)))
        if lead:
            vertex=-(f(Fraction(1))-f(Fraction(-1)))/(4*lead)
            if lo<vertex<hi: values.append(f(vertex))
        return all(v>0 for v in values)
    need(positive_quadratic(mbv-dw,mbv+dw,rq) and
         positive_quadratic(1-mbv-dw,1-mbv+dw,lambda q:rq(1-q)),
         "group-B contact convexity")


class Gaps:
    def __init__(self):
        self.ht, self.hpt = h(Q(TA)), hp(Q(TA))
        self.hct, self.hcpt = hc(Q(TC)), hcp(Q(TC))

    def a1(self,w): return Q(AA)+Q(BA)*w-Q(C1P)*h(w)
    def a1p(self,w): return Q(BA)-Q(C1P)*hp(w)
    def a2(self,w):
        return Q(AA)+Q(BA)*w+Q(C1)*h(w)-self.ht-self.hpt*(w-Q(TA))
    def a2p(self,w): return Q(BA)+Q(C1)*hp(w)-self.hpt
    def c1(self,w): return Q(AC)-Q(BA)*w-Q(C1P)*hc(w)
    def c1p(self,w): return -Q(BA)-Q(C1P)*hcp(w)
    def c2(self,w):
        return Q(AC)-Q(BA)*w+Q(C1)*hc(w)-self.hct-self.hcpt*(w-Q(TC))
    def c2p(self,w): return -Q(BA)+Q(C1)*hcp(w)-self.hcpt
    def bv(self,w): return Q(IV0)+Q(SV)*w-fv(w)
    def bvp(self,w): return Q(SV)-fvp(w)
    def bu(self,w): return Q(IU0)-Q(SV)*w-fu(w)
    def bup(self,w): return -Q(SV)-fup(w)


def abs_hi(x): return max(x.lo.copy_abs(), x.hi.copy_abs())


def tangent_floor(f, fp, middle, radius):
    value, deriv = f(Q(middle)), fp(Q(middle))
    floor = DOWN.subtract(value.lo, UP.multiply(abs_hi(deriv), radius))
    need(value.lo > 0 and floor > 0, "contact tangent bound")
    return floor


def endpoint_floor(f, left, right):
    a, b = f(Q(left)).lo, f(Q(right)).lo
    need(a > 0 and b > 0, "concave endpoint bound")
    return min(a, b)


def cover(f, fp, left, right, endpoint_derivative=False):
    stack, accepted, depth_max, worst = [(left,right,0)], 0, 0, None
    while stack:
        x,y,depth=stack.pop()
        need(depth <= 110 and UP.subtract(y,x) >= D("1e-40"),
             "unresolved interval cell")
        cell, value = IV(x,y), f(IV(x,y))
        if value.lo > 0:
            margin=value.lo
        else:
            mid=NEAR.divide(NEAR.add(x,y),D(2))
            need(x < mid < y, "noninterior subdivision midpoint")
            margin=None
            if endpoint_derivative or (x>0 and y<1):
                # Bound distance from the *computed* midpoint rather than
                # assuming its rounded value is the exact arithmetic midpoint.
                width=max(UP.subtract(mid,x),UP.subtract(y,mid))
                margin=DOWN.subtract(f(Q(mid)).lo,
                                     UP.multiply(abs_hi(fp(cell)),width))
            if margin is None or margin <= 0:
                stack.extend(((x,mid,depth+1),(mid,y,depth+1)))
                continue
        accepted += 1
        need(accepted <= 500000, "cell budget")
        depth_max=max(depth_max,depth)
        worst=margin if worst is None else min(worst,margin)
    return accepted, depth_max, worst


def certify():
    exact_audit()
    g=Gaps()
    phi_a=g.ht+(ONE-Q(TA))*g.hpt
    phi_c=g.hct-Q(TC)*g.hcpt
    need(phi_a.lo>0 and phi_c.lo>0, "global inner tangent lemma")

    floors=[
        tangent_floor(g.a1,g.a1p,MA0,max(UP.subtract(TA,MA0),MA0)),
        endpoint_floor(g.a2,TA,CI),
        tangent_floor(g.a2,g.a2p,MA1,WIN),
        tangent_floor(g.c1,g.c1p,MC1,max(UP.subtract(MC1,TC),
                                        UP.subtract(D(1),MC1))),
        endpoint_floor(g.c2,DOWN.subtract(D(1),CI),TC),
        tangent_floor(g.c2,g.c2p,MC0,WIN),
        tangent_floor(g.bv,g.bvp,MBV,WIN),
        tangent_floor(g.bu,g.bup,MBU,WIN),
    ]
    segments=(
        (g.a2,g.a2p,CI,DOWN.subtract(MA1,WIN),False),
        (g.a2,g.a2p,UP.add(MA1,WIN),D(1),False),
        (g.c2,g.c2p,D(0),DOWN.subtract(MC0,WIN),False),
        (g.c2,g.c2p,UP.add(MC0,WIN),DOWN.subtract(D(1),CI),False),
        (g.bv,g.bvp,D(0),DOWN.subtract(MBV,WIN),True),
        (g.bv,g.bvp,UP.add(MBV,WIN),D(1),True),
        (g.bu,g.bup,D(0),DOWN.subtract(MBU,WIN),True),
        (g.bu,g.bup,UP.add(MBU,WIN),D(1),True),
    )
    covers=[cover(*s) for s in segments]
    value=(Q(C1P)*(iy(HALF)+iz(HALF))+
           Q(AA)+Q(BA)*HALF+Q(AC)-Q(BA)*HALF+
           Q(IU0)-Q(SV)*HALF+Q(IV0)+Q(SV)*HALF)
    need(value == EXPECTED_VALUE, "final interval drift")
    need(value.hi <= HEADLINE, "claimed rounded upper bound not certified")
    evidence=(phi_a,phi_c,tuple(floors),tuple(covers),value)
    return value,evidence


def main():
    reference,evidence=certify()
    saved=getcontext().copy()
    try:
        for precision,rounding in ((5,ROUND_UP),(7,ROUND_FLOOR),
                                   (3,ROUND_CEILING)):
            getcontext().prec, getcontext().rounding = precision, rounding
            need(certify()==(reference,evidence), "ambient context leaked")
    finally:
        setcontext(saved)
    cells=sum(x[0] for x in evidence[3])
    depth=max(x[1] for x in evidence[3])
    print("PASS: exact row/tensor audit; continuous D1/D2; all priors;")
    print("      three hostile Decimal contexts identical")
    print("U =",reference)
    print("certified rounded headline =", HEADLINE)
    print("regular interval cover:",cells,"cells; max depth",depth)


if __name__ == "__main__":
    main()
