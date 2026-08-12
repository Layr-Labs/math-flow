# Half-skew BSSC private-message sum-capacity

Consider the binary-input, two-receiver discrete memoryless broadcast channel
with \(X,Y,Z\in\{0,1\}\) and marginal transition matrices, whose rows are
indexed by \(x=0,1\) and columns by the output symbol \(0,1\),

\[
P_{Y|X}=\begin{pmatrix}\tfrac12&\tfrac12\\0&1\end{pmatrix},
\qquad
P_{Z|X}=\begin{pmatrix}1&0\\\tfrac12&\tfrac12\end{pmatrix}.
\]

There are two independent private messages: receiver \(Y\) must decode the
first and receiver \(Z\) the second. There is no common message and no
feedback. A nonnegative rate pair \((R_1,R_2)\) is *achievable* if there is a
sequence of length-\(n\) broadcast codes with message-set sizes
\(2^{n(R_i-o(1))}\) whose average decoding error at both receivers tends to
zero. Only the two displayed marginals affect this private-message capacity;
any fixed joint coupling \(P_{Y,Z|X}\) with those marginals gives the same
objective. All logarithms are base two and rates are in bits per channel use.
Define

\[
C_{\mathrm{sum}}
=\sup\{R_1+R_2:(R_1,R_2)\text{ is achievable}\}.
\]

Determine \(C_{\mathrm{sum}}\), or rigorously improve either side of the
published benchmark interval

\[
0.361642884421954615663441578150587\ldots
\le C_{\mathrm{sum}}\le
0.369316568803963.
\]

The lower endpoint is the randomized-time-division value within Marton's inner
bound. The January 2026 Gohari--Liu--Nair manuscript records the displayed
upper endpoint and reports the smaller numerical value
\(0.369296340638082\) from a simplified two-auxiliary-receiver calculation.
A numerical minimization or finite posterior grid alone does not certify a
converse over every admissible auxiliary law, so the latter decimal is a lead
rather than the governed baseline here.

This problem is ported from `Layr-Labs/bssc-challenge`. Its public `main`
baseline is commit `2e11491b10730ec601cea363cf2565cc13cf2892`. The source
worktree's local `local-yukon/canonical` commit
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c` records later accepted artifacts,
including a fixed-pair continuous certificate
\(C_{\mathrm{sum}}\le0.369296945969202842443\). Those artifacts are candidates
for separate governed contributions; this admission neither copies nor
pre-accepts them.

Useful contributions include:

- an achievable coding scheme with a rigorously evaluated larger sum rate;
- a converse proving a smaller universal upper bound;
- an exact or globally certified optimization of a named inner- or
  outer-bound functional;
- a cardinality, extremal, tensorization, or multiletter theorem with its
  precise scope stated;
- an auditable formal or interval-arithmetic certificate covering every point
  in the claimed continuous domain;
- an independent port and verification of a source-challenge artifact; or
- a reproducible numerical lead or non-finding clearly labeled as non-proof.

## Frontier sources

- Layr Labs,
  [BSSC challenge public baseline](https://github.com/Layr-Labs/bssc-challenge/tree/2e11491b10730ec601cea363cf2565cc13cf2892).
- Amin Gohari, Yi Liu, and Chandra Nair,
  [A Two Auxiliary Receiver Outer Bound to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast Channel](https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf),
  manuscript, 2026-01.
- Yanlin Geng, Varun Jog, Chandra Nair, and Zizhou Vincent Wang,
  [An Information Inequality and Evaluation of Marton's Inner Bound for Binary Input Broadcast Channels](https://arxiv.org/abs/1001.1468),
  IEEE Transactions on Information Theory 59 (2013).
- Varun Jog and Chandra Nair,
  [An information inequality for the BSSC channel](https://arxiv.org/abs/0901.1492),
  2009.
