# Certificate record

## Files and reproducibility

The primary verifier is certify_th9_dual.py. It imports only the sibling module interval_arithmetic.py and Python standard-library modules.

The exact source digests are

~~~text
2b5305d1efa9e2c462e621aaac1ebb27d5099103fb5745d6e9a09f9e036db0a8  certify_th9_dual.py
e440f4034c80ff7453389843a16c3ba5378e22267abb05c7ff8211c80dfbaad3  interval_arithmetic.py
~~~

The recorded run used Python 3.14.6 on macOS arm64:

~~~text
python3 certify_th9_dual.py --audit-ambient-context
~~~

It exited successfully in 2.7 seconds for the primary pass plus three hostile-context passes. The verifier is fail-closed: an uncertain sign, an uncovered interval, an exceeded bisection budget, a broken exact identity, or a changed U enclosure raises an exception instead of printing the certified result.

## Exact statement checked

For

~~~text
G = (0.2068684034, 0.8268635311),
K = (0.1731364689, 0.7931315966),
epsilon = 0.000172556,
~~~

the specified nonnegative combination of six full-Theorem-9 rows is continuously dual feasible for every posterior in [0,1] and every input prior in [0,1]. Therefore

~~~text
C_sum(BSSC 1/2) <= U,

U in
[0.36929694655551972763539254207215872386102502532943886683678450695288358384488448,
 0.36929694655551972763539254207215872386102502532943886683678450695288358384488468].
~~~

## Primary run excerpt

~~~text
phase0_exact_audit: all rational checks passed
  weights >= 0, rate sums = 1, combined tensor == closed form,
  c_Y = c_Z = (1+EPS)/2, c_G = c_K = 0, total line slope = 0,
  region orderings, h''-sign control, B-window convexity: exact

phase1_inner_majorants:
  phi(T_A)   in [2.599502E-31, 2.599502E-31] > 0
  phi_C(T_C) in [2.599502E-31, 2.599502E-31] > 0
  every required A/C tangent dominates its curve on all of [0,1]

phase2_value:
  I_Y(1/2) in
  [0.31127812445913286390969579203913761843013919423063920465818550909417632915423095,
   0.31127812445913286390969579203913761843013919423063920465818550909417632915423114]

  U = B(1/2) in
  [0.36929694655551972763539254207215872386102502532943886683678450695288358384488448,
   0.36929694655551972763539254207215872386102502532943886683678450695288358384488468]

  enclosure width 2.000E-79

phase3_tangent_and_endpoint_bounds:
  six A/C/B convex-window floors are positive
  two concave endpoint pairs are positive

phase4_bisection_segments:
  A2b:      cells=3,  worst margin=3.351367E-4
  A2d:      cells=7,  worst margin=6.941141E-4
  C2d:      cells=7,  worst margin=6.941141E-4
  C2b:      cells=3,  worst margin=3.351367E-4
  BV-left:  cells=49, worst margin=6.192790E-19
  BV-right: cells=9,  worst margin=6.485914E-5
  BU-left:  cells=9,  worst margin=6.485914E-5
  BU-right: cells=49, worst margin=6.192790E-19

CERTIFIED: continuous dual feasibility (D1)+(D2) on [0,1] for all
three auxiliary groups, hence for every input prior q0 and every
Theorem 9 auxiliary structure at the fixed channel pair.

ambient_context_audit: passed
(3 hostile contexts, identical certified value)
~~~

The hostile contexts use process-wide precisions 5, 7, and 3 with ROUND_UP, ROUND_FLOOR, and ROUND_CEILING. Intermediate display rounding varies slightly, as expected, while the internally constructed 80-digit U interval is identical.
