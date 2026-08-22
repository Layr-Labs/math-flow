# Reproducible two-letter Marton search for the half-skew BSSC

## One claim, and its strict boundary

This contribution records a deterministic floating-point search campaign for
a two-letter Marton gain on the governed half-skew BSSC.  The attached source
and [evidence.json](evidence.json) fix the architectures, input data, seeds,
optimizer, iteration counts, diagnostics, and numerical maxima.  Within those
finite runs, no value exceeded the canonical directed lower threshold

\[
\begin{aligned}
0.7232857688439092313268831563011740144159620214477211104074274596056014
&<2L_{\rm RTD}\\
&<0.7232857688439092313268831563011740144159620214477211104074274596056016.
\end{aligned}
\]

by more than the declared \(10^{-12}\)-bit comparison tolerance.  The closest
values are replays of the product randomized-time-division basin and differ
from the displayed threshold only at ordinary binary64 rounding scale.  The
best nontrivial escape run was \(3.34660062416488\times10^{-8}\) bits below
the comparison value.

This is **negative numerical evidence only**.  It is not a proof of Marton
additivity, not an upper bound on \(M(P^{\otimes2})\), not a capacity converse,
and not a claim that the global optimizer lies within the tested
cardinalities.  In particular, the inactive-gradient diagnostics at sparse
points are not KKT certificates.

The August 2026 external-source and repository-replay provenance comes from
canonical transaction
f6ea30479b9ca461294ba89a8a1a31c06ce59d08.  Its primary judgment was
indeterminate, so it is not used to certify the threshold.  The exact RTD
formula and directed interval above come from valid foundation transaction
88a1004f309460f3ec1cacdae88d30f88559f9bc.  [claims.json](claims.json)
declares both references in ledger order and assigns them only these roles.
This contribution advances registered direction
bssc-multiletter-marton-frontier; the direction transaction is provenance,
not a logical premise.

## Smooth objective and receiver-skew reflection

For a finite law

\[
(U,V,W)-X^2-(Y^2,Z^2),
\]

write

\[
\begin{aligned}
E_Y&=I(W;Y^2)+I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),\\
E_Z&=I(W;Z^2)+I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W).
\end{aligned}
\]

The search maximizes the smooth half-weight functional

\[
L_{1/2}=\frac12(E_Y+E_Z).
\]

For the half-skew BSSC, complementing both input bits exchanges the receiver
laws up to fixed bijective output complementation.  Reflect a candidate by
that complement, swap \(U,V\), and swap the receiver labels.  Fairly
time-share the original and reflected laws, putting the selector \(Q\) into
\(W\).  The resulting two endpoints are equal; each is the original
\((E_Y+E_Z)/2\) plus the nonnegative selector term
\(I(Q;Y^2)=I(Q;Z^2)\).  Thus the balanced objective is at least the original
\(L_{1/2}\).  Conversely,
\(\min(E_Y,E_Z)\leq(E_Y+E_Z)/2\).  Therefore the optimized two-letter Marton
value equals the optimized \(L_{1/2}\), even though an individual law need
not be balanced.  A strict \(L_{1/2}\) witness would consequently be enough;
branch balance was not imposed during local optimization.

The implementation evaluates \(L_{1/2}\), in nats, by the entropy identity

\[
\frac12H(Y^2)+\frac12H(Z^2)
+\frac12H(W,Y^2)+\frac12H(W,Z^2)
-H(W,U,Y^2)-H(W,V,Z^2)+H(W,U,V).
\]

The analytic gradient of this expression was checked in a random interior
direction.  The finite-difference residual was
\(4.586475643719723\times10^{-11}\) nats.  The later escape campaign also
recomputed both endpoints separately and compared their average with the
simplified expression; the largest discrepancy was
\(8.881784197001252\times10^{-16}\) nats.

## Frozen campaign

All objectives below are bits per two channel uses.

| campaign | exact finite coverage | best optimized output |
| --- | --- | ---: |
| Published-architecture transplant | two exact \(2\times4\times4\times9\) component laws times every \(4^9\) deterministic relabeling, 524,288 evaluations | 0.5451904011322217 |
| Full joint \(W=U=V=4\) | 48 seeds, 20,000 Adam steps each, all 256 probabilities \(p(w,u,v,x^2)\) | 0.7232857688438281 |
| Full joint \(W=8,U=V=4\) | 24 seeds, 30,000 steps each, all 512 probabilities | 0.7232857688438825 |
| Transplant continuation | 24 raw plus 24 fair-reflected starts, 30,000 steps each | 0.7131610038323559 |
| Product/nonrectangular homotopy | 11 weights, independent chord plus forward and reverse continuation, 33 runs of 15,000 steps | 0.7232857688438992 |
| Symmetry-reduced fixed input | 15 values of \(a\), six starts and 20,000 constrained steps per value, where \(p_X=(a,\frac12-a,\frac12-a,a)\) | 0.7232857688439037 |
| Orthogonal and map-mutated escape | six weights, 13 runs per weight: one base, six chord-orthogonal, three \(X\)-map mutations, three \(W=8\) lifts; 78 runs | 0.7232857353779031 |
| Three-symbol-face stress check | 5,000 random laws and 12 local optimizations on each of four faces | maximum proposed-bound violation \(-0.026075082275836367\) |

The product-basin values in the middle rows should be read as equality within
floating-point error, not as strict upper or lower comparisons to the exact
threshold.  Separately evaluating the exact product seed in binary64 returned
0.723285768843912 bits, an apparent
\(2.77\times10^{-15}\)-bit overshoot that is included in the verifier's
conservative directed-lower-endpoint tolerance audit and is not a strict gain.

### Exhaustive nonrectangular transplant

The source data are the two exact rational component laws in
data/certificates/fixed_input/cc_certificate_e5e-7.json at immutable external
Git commit cc33e854cb1c5e99cb18fe500f60a529fce136f8.  The file SHA-256 is

    45502b2e7a694ae2d1beaee3e19249d63d9efe39b6405daa42ada0e1cbb846d6

Only this data file was read; no external program participates in the
transplant scan.  For each component law, every map from its nine input labels
to the four BSSC super-inputs was evaluated.  Source row 7 attained its maximum
at map

    (1, 0, 3, 0, 0, 2, 3, 2, 3)

with base-4 map identifier 243761.  Its endpoints were
0.5465257842796067 and 0.5438550179848367 bits.  The extended replay checks
coordinatewise-separable maps in both orientations: first-bit row/second-bit
column and first-bit column/second-bit row.  For source row 6 the two maxima
are both 0.4684740866886777; for source row 7 they are
0.46858123463677875 and 0.4685812346367781.  Thus the union maximum is
0.46858123463677875.  The row-7 maxima by image size one through four were

    -0.013359000186186187
     0.4872419126848573
     0.5025068963908965
     0.5451904011322217

Fair receiver-skew reflection raises both endpoints of this raw candidate to
0.653605122467966689225950638221927866... bits.  The attached independent
Fraction/100-digit Decimal implementation checks both the direct
mutual-information formula and the entropy formula.
The exhaustive binary64 maximum differs from the 100-digit recomputation from
the same exact rational law and map by
\(1.120898227443350889\ldots\times10^{-15}\) bits; the two endpoint
differences are each below \(1.5\times10^{-15}\) bits.

As a separate diagnostic against the correlation residual identity in
canonical transaction
5ed3f525b9ae7f32c6e1dcbf22ecdb5ae946a4a6, the exact raw law has left side
0.350903397111423894537025260768407150..., right side
0.002273937373006149666264462449949631..., and difference
0.348629459738417744870760798318457519....  The fair-reflected law has the
same left side, right side
0.002022370956426087316564125541104552..., and difference
0.348881026154997807220461135227302599....  The defining identity closes to
\(-5\times10^{-100}\) and \(0\times10^{-99}\), respectively.

The four constant-padding correlation screens reject the raw law through
slack \(-0.00772526452650419\ldots\), while all four reflected-law slacks are
positive.  Because the reflected law still lies far below RTD, this also
demonstrates numerically that passing all four necessary screens is not
sufficient for gain.  Full 75-digit entries are frozen in evidence.json and
recomputed by scratch_transplant_audit.py.

### Full-joint stochastic searches

The \(W=U=V=4\) campaign used seeds

\[
2026082201+104729i,\qquad 0\leq i<48.
\]

Runs 0--23 began at product RTD mixed with uniform mass
\(10^{-8+6i/23}\), followed by Gaussian logit noise of standard deviation
\(0.35+0.12i\).  Runs 24--47 used independent \(N(0,1.5)\) logits.  Adam used
\((\beta_1,\beta_2)=(0.9,0.999)\), denominator epsilon \(10^{-14}\), initial
rate 0.08, the source's quadratic decay, gauge-centering, and a \(-90\) logit
floor.

The best run, seed 2026082201, returned 0.7232857688438281 bits with simplex
residual \(2.22\times10^{-16}\), 36 cells above \(10^{-10}\), active-gradient
spread \(4.0634\times10^{-8}\) nats, and inactive excess
\(9.4577\times10^{-5}\) nats.  The last number is why this is not presented as
a local-optimality certificate.  The best independently initialized interior
run was seed 2029433529 at 0.7191671066492605 bits.

The \(W=8,U=V=4\) replay used the same seed formula for 24 starts, initial rate
0.07, and 30,000 steps.  Its best product-family value was
0.7232857688438825.  The best fully interior start, seed 2028072052, returned
0.7232857670813002.

### Nonrectangular continuation and hysteresis

The exact transplanted law and its fair reflection seeded 24 runs each, with
seeds \(2026082251+130363i\), uniform mixing from \(10^{-7}\) to \(10^{-2}\),
Gaussian logit noise \(0.15+0.04i\), rate 0.06, and 30,000 steps.  The best raw
value was 0.6798006361040297.  The best reflected value, seed 2029080600, was
0.7131610038323559.  It has full input support and a distinct input
distribution

    (0.2108453, 0.3047181, 0.3047178, 0.1797188).

Auxiliary relabeling aligned this basin to product RTD with Hellinger affinity
0.4622976013230229 and total variation 0.6481544978162777.  The complete
three-way homotopy table is frozen in evidence.json.  Forward continuation
jumped to the product basin between weights 0.3 and 0.4.  Reverse continuation
remained near product through weight 0.2 and fell to the lower branch between
0.2 and 0.1.  This hysteresis is evidence for multiple local basins, but the
nonrectangular basin stayed below product.

The subsequent escape search perturbed weights 0.25 through 0.50 in directions
orthogonal to the product/nonrectangular logit chord, mutated conditional
input maps, and split \(W\) to cardinality eight.  Its best run was the
\(W=8\), weight 0.40, seed 2026385028, mutation-amount 0.75 candidate:

    L_1/2       0.7232857353779031
    residual   -0.0000000334660062416488
    endpoints   0.7232856516789663, 0.7232858190768404
    p(X^2)      0.2500004133109376, 0.24999853769565314,
                0.25000143682450543, 0.24999961216890318

Every escape candidate retained all four super-inputs; the smallest input mass
seen anywhere in that batch was 0.17566030256827508.

### Fixed-input and face screens

The symmetry-reduced fixed-input sweep covered

    a = .02,.05,.10,.15,.20,.23,.24,.25,.26,.27,.30,.35,.40,.45,.48.

At each value it optimized the full conditional law
\(p(w,u,v\mid x^2)\) from product, reflected, and four random starts.  The
maximum was at \(a=1/4\), equal to the product value at float precision.
Every other grid point was lower; the complete maxima are in evidence.json.

As an adversarial validation of a separate analytic candidate, the face
screen tested

\[
M(p)\leq \frac12[I(X^2;Y^2)+I(X^2;Z^2)]
+2\{h_2(1/4)-3/4\}
\]

on all four three-symbol faces.  It used 20,000 random full Marton laws in
total, 48 local optimizations, and projected product/raw/reflected candidates.
The largest numerical violation was negative:
\(-0.026075082275836367\) bits.  This is a sign/scope stress test only; it is
not the analytic proof of that inequality.

## Reproduction

The governed verifier is standard-library only and does not rerun the costly
nonconvex campaign:

~~~bash
python3 -I -B verify.py
~~~

It checks the frozen source hashes, finite coverage arithmetic, seed formulas,
all recorded comparisons, endpoint averaging, full-input-support statements,
the complete homotopy arrays, and the negative three-face diagnostic.

The executed search environment was Python 3.13.1 and NumPy 2.4.3.  To replay
the transplant-dependent runs, first obtain the audited data at the exact path
expected by the frozen discovery source:

~~~bash
git clone https://github.com/yanxiaoliu-mike/Suboptimality_Marton \
  /tmp/Suboptimality_Marton-audit-jdichc
git -C /tmp/Suboptimality_Marton-audit-jdichc checkout \
  cc33e854cb1c5e99cb18fe500f60a529fce136f8
sha256sum /tmp/Suboptimality_Marton-audit-jdichc/data/certificates/fixed_input/cc_certificate_e5e-7.json
~~~

Then run from the search directory:

~~~bash
python3 -B scratch_transplant_scan.py --batch 4096 --top 12
python3 -B scratch_transplant_audit.py
python3 -B scratch_stochastic_marton.py --seeds 48 --iterations 20000
python3 -B scratch_stochastic_marton.py --nw 8 --seeds 24 \
  --iterations 30000 --lr 0.07
python3 -B scratch_transplant_opt.py --seeds 24 \
  --iterations 30000 --lr 0.06
python3 -B scratch_transplant_opt.py --raw --seeds 24 \
  --iterations 30000 --lr 0.06
python3 -B scratch_homotopy.py --steps 10 --iterations 15000 --lr 0.05
python3 -B scratch_fixed_input_search.py \
  --iterations 20000 --random-starts 4
python3 -B scratch_jump_escape.py \
  --iterations 18000 --orthogonal 6 --w8 3
python3 -B scratch_three_face_bound.py \
  --random 5000 --starts 12 --iterations 15000
~~~

The full rerun is intentionally expensive.  Runtime variation and last-digit
floating variation may occur across BLAS/NumPy platforms.  A positive lead
would require an independently evaluated finite law followed by directed or
exact certification before it could support a strict mathematical claim.
