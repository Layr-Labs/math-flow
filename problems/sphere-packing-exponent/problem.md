# High-dimensional sphere-packing exponent

Let \(\Delta_d\) be the supremal upper density of a packing of congruent
balls in Euclidean space \(\mathbb R^d\). Scaling the balls does not change
\(\Delta_d\). Define the base-two exponential decay parameter

\[
\beta_{\mathrm{pack}}
=\liminf_{d\to\infty}-\frac1d\log_2\Delta_d.
\]

Determine \(\beta_{\mathrm{pack}}\), raise its certified lower bound by
proving a stronger universal packing-density upper bound, or lower its
certified upper bound by constructing denser packings. The August 2026 OpenAI
Astra manuscript claims the interval

\[
\frac12\log_2\!\left(\frac{2\pi}{e}\right)
=0.6044005442916777\ldots
\le \beta_{\mathrm{pack}}\le 1.
\]

The right endpoint follows from classical asymptotic constructions. Before
the Astra announcement, the Kabatianskii--Levenshtein method gave the lower
endpoint \(0.59905576\ldots\). Astra also claims that
\(\tfrac12\log_2(2\pi/e)\) is the exact exponential strength of the
Cohn--Elkies linear-programming framework; that framework limit is not a
determination of the true packing exponent. The new result is very recent, so
its reproduction or independent audit is itself useful. All cited claims are
external background rather than Math Flow ledger evidence.

Useful contributions include:

- an independent proof or formal replay of the announced \(0.6044005\ldots\)
  lower bound;
- a stronger asymptotic upper bound on \(\Delta_d\), with every optimization
  and limiting step certified;
- a packing construction proving \(\Delta_d\ge 2^{-(c+o(1))d}\) for some
  \(c<1\);
- a theorem establishing a sharp barrier for a precisely defined relaxation;
- exact or interval-arithmetic certificates for finite-dimensional programs,
  together with the proof that they imply the asymptotic claim; or
- reproducible numerical evidence clearly labeled as non-proof.

## Frontier sources

- OpenAI,
  [Ten new results in mathematics](https://openai.com/index/ten-advances-in-mathematics/),
  2026-08-01.
- OpenAI,
  [Astra mathematics manuscripts](https://cdn.openai.com/pdf/ten-proofs-oai.pdf),
  revised 2026-08-06; see the sphere-packing chapter.
- Henry Cohn and Noam Elkies,
  [New upper bounds on sphere packings I](https://arxiv.org/abs/math/0110009),
  Annals of Mathematics 157 (2003).
