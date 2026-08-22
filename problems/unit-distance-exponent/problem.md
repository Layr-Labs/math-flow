# Planar unit-distance exponent

For an integer \(n\ge 2\), let \(u(n)\) be the maximum, over all sets of
\(n\) distinct points in \(\mathbb R^2\), of the number of unordered pairs
whose Euclidean distance is exactly \(1\). Define

\[
\alpha_{\mathrm{UD}}
=\limsup_{n\to\infty}\frac{\log u(n)}{\log n}.
\]

Determine \(\alpha_{\mathrm{UD}}\), improve its certified lower bound, or
improve its certified upper bound. A conservative published interval is

\[
1.0152\le \alpha_{\mathrm{UD}}\le \frac43.
\]

The upper endpoint follows from the classical \(O(n^{4/3})\) incidence bound.
In May 2026 an OpenAI-discovered construction first established
\(\alpha_{\mathrm{UD}}>1\), disproving the conjectured
\(u(n)=n^{1+o(1)}\) growth. Sawin then gave an explicit human-written
certificate with exponent above \(1.014\), and Emmerich published a
reproducible optimization supporting the displayed \(1.0152\) baseline.
These external results are background, not pre-existing Math Flow
contributions.

Useful contributions include:

- an infinite construction with a rigorously derived larger exponent;
- an auditable number-field or integer-optimization certificate together with
  exact verification code;
- an incidence-theoretic argument lowering the \(4/3\) upper endpoint;
- a formalization or independent reconstruction of a claimed construction;
- a finite construction only when its asymptotic implication is proved; or
- a reproducible search result or obstruction with its restricted scope
  clearly stated.

Floating-point optimization alone is a lead, not a proof of an asymptotic
bound. Computational submissions should include the exact data and the
analytic implication from that data to the claimed exponent.

## Frontier sources

- OpenAI,
  [A model disproves a long-standing conjecture in discrete geometry](https://openai.com/index/model-disproves-discrete-geometry-conjecture/),
  2026-05-20, with the linked proof manuscript.
- Will Sawin,
  [An explicit lower bound for the unit distance problem](https://arxiv.org/abs/2605.20579),
  2026.
- Michael T. M. Emmerich,
  [Optimizing Explicit Unit-Distance Lower-Bound Certificates](https://arxiv.org/abs/2606.03419),
  2026.
