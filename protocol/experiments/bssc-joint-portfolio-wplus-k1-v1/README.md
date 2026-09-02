# BSSC joint portfolio/W+ K1 experiment

This is an unpublished, publication-forbidden experiment. It tests whether
giving one judge both the downstream accounting semantics and responsibility
for the new live `W+` state improves the K1 program breakout.

The accepted intermediate-result semantics are frozen before the model call.
The experimental provider may choose only:

- the program hierarchy;
- placement of the two fixed results;
- an explicit accounting boundary for every program; and
- complete primitive `W+` annotations (`directWorkHours` and child
  `conditionalIncidence`).

The provider never sees or authors `W-`, `D`, payout, percentages, contributor
credit, global reach, subtree totals, or prior-credit corrections. Trusted code
derives a valid state-v3 knowledge transition, reduces it, and applies the
unchanged work-accounting reducer. The first gate is the existing K1 relational
gold: one narrow parent plus two independently estimable leaves. K2 remains a
holdout and is not dispatched unless K1 passes.

This first version is intentionally K1-only. It establishes the joint contract
without prematurely designing the local/fractal read/write protocol required
for later submissions.
