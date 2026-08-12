# Simple zeta zeros on the critical line

Write each nontrivial zero of the Riemann zeta function as
\(\rho=\beta+i\gamma\). Let \(N(T,2T)\) count the zeros with
\(T<\gamma\le 2T\), including multiplicity, and let
\(N_0^s(T,2T)\) count those zeros that are simple and satisfy
\(\beta=\tfrac12\). Define

\[
\kappa_s
=\liminf_{T\to\infty}\frac{N_0^s(T,2T)}{N(T,2T)}.
\]

Determine \(\kappa_s\), or prove an unconditional lower bound larger than

\[
c_{\mathrm C}
=\frac32-\frac1{\sqrt2}\cot\!\left(\frac1{\sqrt2}\right)
=0.672500703679\ldots.
\]

The universal upper bound is \(\kappa_s\le1\). The previously published
record was strictly greater than \(5/12\). A Claude-generated manuscript
announced on 2026-08-10 claims \(\kappa_s\ge c_{\mathrm C}\), as well as the
same constant for distinct critical-line zeros, and supplies a Lean
formalization. This result is too recent to have ordinary journal review, so
an independent analytic or formal replay is a valuable first target. The
claim is external background and is not Math Flow ledger evidence until
submitted and judged here.

This is a critical-line density problem, not the Riemann hypothesis. The cited
claim does not locate or constrain the remaining roughly \(32.75\%\) of zeros
and does not imply that the Riemann hypothesis is "67 percent solved."
Conditional results may be submitted only when their assumptions and effect
on the unconditional objective are labeled explicitly.

Useful contributions include:

- an independent proof or a reproducible, sorry-free replay of the claimed
  \(c_{\mathrm C}\) bound;
- a mollifier or pair-correlation argument proving a larger constant;
- an exact optimization certificate for a precisely defined test-function
  family, with the analytic reduction proved;
- a rigorous ceiling for a named method or bandwidth restriction;
- a formalization of a missing analytic input; or
- numerical optimization clearly separated from an unconditional theorem.

## Frontier sources

- Anthropic,
  [Advancing mathematics with Claude](https://www.anthropic.com/research/riemann-zeta),
  2026-08-10.
- Claude,
  [More than two thirds of the zeros of the Riemann zeta function lie on the critical line](https://www-cdn.anthropic.com/564f962e60643842f5fcb4a17c9dbc8f608f1c37.pdf),
  2026-08-10.
- Anthropic,
  [Formalization repository at tag v1.0](https://github.com/anthropics/zeta-23-lean/tree/3635e74826a4c1fcece7d1cd2b6fa75e43a00510).
- Kyle Pratt, Nicolas Robles, Alexandru Zaharescu, and Dirk Zeindler,
  [More than five-twelfths of the zeros of zeta are on the critical line](https://arxiv.org/abs/1802.10521),
  Research in the Mathematical Sciences 7 (2020).
