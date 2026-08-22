# Marton multiletter frontier audit for the half-skew BSSC

## Claim and exact scope

Let \(P\) be the governed binary-input half-skew BSSC.  For \(n\geq 1\),
regard \(P^{\otimes n}\) as one finite broadcast **super-channel**, and define
the unnormalized private-message Marton sum functional, in bits per
super-channel use,

\[
M_n(P):=\sup_{(U,V,W)-X^n-(Y^n,Z^n)}
\left[
\min\{I(W;Y^n),I(W;Z^n)\}
+I(U;Y^n\mid W)+I(V;Z^n\mid W)-I(U;V\mid W)
\right].
\]

Then

\[
\boxed{C_{\mathrm{sum}}(P)\geq \frac1n M_n(P)\quad(n\geq 1).}
\]

The multiletter sequence is superadditive:

\[
M_{m+n}(P)\geq M_m(P)+M_n(P)\qquad(m,n\geq 1).
\]

Consequently, Fekete's lemma gives the canonical asymptotic target

\[
\boxed{
C_{\mathrm{sum}}(P)
\geq \lim_{n\to\infty}\frac{M_n(P)}n
=\sup_{n\geq 1}\frac{M_n(P)}n.
}
\]

Let \(L_{\mathrm{RTD}}\) be the exact randomized-time-division value, which the
binary-input evaluation of Marton's inner bound identifies with \(M_1(P)\).
Such an \(n\)-letter Marton witness of value \(S_n\) strictly improves the
one-letter Marton lower bound if and only if

\[
S_n>nL_{\mathrm{RTD}}.
\]

For \(n=2\), the exact threshold is \(2L_{\mathrm{RTD}}\).  Its decimal display
begins

\[
2L_{\mathrm{RTD}}
=0.723285768843909231326883156301174\ldots.
\]

This turns the August 2026 general-channel result into a precise BSSC research
test.  It does **not** assert that a BSSC witness above this threshold is
currently known.

This contribution advances canonical direction
`bssc-multiletter-marton-frontier`, registered by transaction
`7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.  That registration records the
research-program alignment and priority trail; it is not a mathematical
premise, so `claims.json` correctly leaves `dependencyTransactionIds` empty.

## Proof of the super-symbol and asymptotic reductions

Fix \(n\) and \(\epsilon>0\).  Choose finite auxiliaries for the super-channel
\(P^{\otimes n}\) whose Marton sum is at least \(M_n(P)-\epsilon\).  Marton's
ordinary one-letter coding theorem, applied to this finite super-channel,
gives codes over \(\ell\) independent super-channel uses with asymptotic sum rate
at least \(M_n(P)-\epsilon\) bits per super-use.  The same code is an ordinary
BSSC code of blocklength \(\ell n\).  Its sum rate per original channel use is at
least

\[
\frac{M_n(P)-\epsilon}{n}.
\]

First let the coding blocklength \(\ell\to\infty\), then let
\(\epsilon\downarrow0\).  This proves the displayed bound.  No attainment of
the supremum defining \(M_n(P)\) is needed.

For superadditivity, choose independent \(\epsilon\)-optimal Marton laws at
blocklengths \(m\) and \(n\).  For either constituent law, write

\[
A_r=I(W_r;Y^r),\qquad B_r=I(W_r;Z^r),
\]

and let \(R_r\) denote its remaining three private-message terms, for
\(r\in\{m,n\}\).  Concatenate the two laws independently and take the new
auxiliaries to be the corresponding ordered pairs.  This is an admissible law
for \(P^{\otimes(m+n)}\).  Independence makes every conditional private term
add, so its private remainder is \(R_m+R_n\), while its two common-message
informations are \(A_m+A_n\) and \(B_m+B_n\).  The only inequality needed is

\[
\min\{A_m+A_n,B_m+B_n\}
\geq \min\{A_m,B_m\}+\min\{A_n,B_n\}.
\]

The concatenated objective is therefore at least the sum of the two
constituent objectives.  Letting \(\epsilon\downarrow0\) proves
\(M_{m+n}(P)\geq M_m(P)+M_n(P)\).

Constant auxiliaries show \(M_n(P)\geq 0\).  Conversely, drop the nonpositive
term and bound the common term by its \(Y^n\) branch to get

\[
M_n(P)
\leq H(Y^n)+H(Z^n)
\leq 2n\quad\text{bits}
\]

for this binary-output BSSC.  Thus the sequence is finite and grows at most
linearly.  Fekete's lemma gives
\(\lim_n M_n(P)/n=\sup_n M_n(P)/n\); combining this with the super-symbol
bound for every \(n\) proves the asymptotic boxed inequality above.

More concretely, \(k\) independent copies of any fixed \(n\)-letter witness
of value \(S_n\) form a \(kn\)-letter witness of value exactly \(kS_n\): both
common-message informations and every private term scale by \(k\).  Hence any
strict finite-blocklength Marton gain propagates to every positive multiple
of that blocklength and forces the asymptotic Marton rate above
\(L_{\mathrm{RTD}}\).

For the BSSC, put \(q=P(X=0)\),

\[
J(q)=h_2(q/2)-q,
\qquad
h_2(t)=-t\log_2t-(1-t)\log_2(1-t).
\]

Write \(D(q)=J(q)-J(1-q)\).  The exact randomized-time-division variational
value is

\[
L_{\mathrm{RTD}}
=J(1/2)+\frac12\max_{0\leq q\leq 1}\{J(q)-J(1-q)\}.
\]

For \(0<q<1\), direct differentiation gives

\[
D'(q)
=\frac12\log_2\!\left(\frac{(2-q)(1+q)}{q(1-q)}\right)-2.
\]

All factors inside the logarithm are positive, so \(D'(q)>0\) is equivalent
to

\[
(2-q)(1+q)>16q(1-q)
\quad\Longleftrightarrow\quad
15q^2-15q+2>0.
\]

The two stationary points are

\[
q_{\pm}=\frac{15\pm\sqrt{105}}{30}.
\]

The upward-opening quadratic is positive outside \([q_-,q_+]\) and negative
inside.  Moreover, \(D(1-q)=-D(q)\) and
\(D(0)=D(1/2)=D(1)=0\).  Hence \(D\) increases from zero to its global
maximum at \(q_-\), decreases to its reflected global minimum at \(q_+\),
and then increases back to zero.  Therefore

\[
\boxed{
L_{\mathrm{RTD}}
=h_2(1/4)-\frac12
+\frac12\left[
h_2(q_-/2)-h_2((1-q_-)/2)+1-2q_-
\right],
\qquad
q_-=\frac{15-\sqrt{105}}{30}.
}
\]

The classical binary-input Marton evaluation cited in the problem statement
identifies \(M_1(P)=L_{\mathrm{RTD}}\); that external theorem is a declared
premise here, not re-proved.  The governed decimal
\(0.361642884421954615663441578150587\ldots\) is a display of this value.
`verify_audit.py` evaluates the boxed closed form with 100-digit standard-library
decimal arithmetic, checks the stationary quadratic and its sign pattern, and
then checks both 33-digit displays.  Because the displays have ellipses, those
digits are **not** directed upper enclosures.  A strict computational witness
must compare against the exact closed form or against a separately certified
upper enclosure for it.

Equality \(M_n(P)=nL_{\mathrm{RTD}}\), or failure to find a strict witness, at
any one fixed \(n\) only closes that particular Marton blocklength.  It is not
a converse for BSSC capacity: another blocklength or a non-Marton coding
scheme could still do better.

## Immutable August 2026 source audit

The following theorem descriptions are external-source declarations checked
against immutable arXiv v1 pages and downloaded PDFs.  This contribution does
not independently prove the papers' analytic theorems.  Exact URLs, submission
timestamps, PDF byte sizes, SHA-256 digests, and structured theorem summaries
are in `source_manifest.json`.

### Huang--Liu--Liu, 20 August 2026

[Sub-optimality of Marton's Inner Bound for the Two-Receiver Broadcast
Channel, arXiv:2608.19869v1](https://arxiv.org/abs/2608.19869v1) was submitted
at `2026-08-20T10:27:59Z`.  The audited PDF URL is
<https://arxiv.org/pdf/2608.19869v1>; its downloaded bytes have SHA-256
`0c67e0b283be1b61c72cfff3c1870cf73f06233ea33bafeb5c6fc5b2a4f1ceca`.

- Theorem 4 (constraint removal) assumes a finite broadcast channel \(T\), a
  finite concave upper bound \(f\) on its fixed-input Marton functional, a
  prescribed \(p^*\), and a two-letter witness whose two coordinate input
  marginals average to \(p^*\) and whose value is \(>2f(p^*)\).  It concludes
  that some finite unconstrained channel \(T'\) obeys
  \(M_{T'^{\otimes2}}>2M_{T'}\).
- Theorem 5 asserts existence of a finite two-receiver DMBC
  \(\widetilde T\) with
  \(M_{\widetilde T^{\otimes2}}>2M_{\widetilde T}\), and consequently strict
  containment of its complete one-letter Marton region in its capacity
  region.
- The certified base construction has ternary input.  The fully explicit
  unconstrained lift has input alphabet
  \(\{0,1,2\}\times[N]\), with \(N=2^M\) and \(M=2{,}000{,}000\), hence input
  cardinality \(3\cdot2^{2{,}000{,}000}\).  It is not a binary-input example.
- The paper says counterexamples *appear* to require nonbinary input; this is
  an observation about the search, not a theorem.  Its conclusion explicitly
  leaves binary-input Marton tightness open.

Therefore Theorem 5 changes the global research interpretation--universal
one-letter Marton optimality and universal self-additivity are false--but it
does not change the BSSC lower endpoint.  It supplies a compelling
multiletter direction, whose exact BSSC success criterion is the threshold
proved above.

### Liu--Huang, 13 August 2026

[Counterexamples to the Markovity Conjecture for the Two-Receiver Broadcast
Channel, arXiv:2608.13170v1](https://arxiv.org/abs/2608.13170v1) was submitted
at `2026-08-13T12:39:09Z`.  The audited PDF URL is
<https://arxiv.org/pdf/2608.13170v1>; its downloaded bytes have SHA-256
`313c49fab92c69efb108d706101a3357276e88097e378083272c573a37f11c92`.

- Theorem 1 reduces the literal finite-alphabet Markov class \(U-X-V\) at
  fixed input marginal to \(|U'|,|V'|\leq |X|\), without decreasing the dual
  objective, and establishes attainment of that constrained supremum.
- Theorem 2 assumes finite input, strictly positive receiver marginals,
  irreducibility (no duplicate pair of receiver-marginal rows), a fixed
  potential vector, and \(0<\alpha<1\).  Under those assumptions, existence
  of a Markov global optimizer is equivalent to existence of a deterministic
  rectangular global optimizer.
- Both certified counterexamples are strictly positive ternary-input,
  ternary-output channels using a nonrectangular \(2\times2\) auxiliary
  pattern.  The second separation is at least
  \(2.711224394247\times10^{-11}\) nats.
- That paper explicitly says its counterexamples neither invalidate Marton's
  achievable region nor resolve the separate additivity conjecture.  The
  latter was resolved for a different, nonbinary channel by the 20 August
  paper.

The BSSC has a binary input and zero entries in both receiver transition
matrices.  Thus the two ternary counterexamples are not BSSC examples, and the
strict-positivity hypothesis of Theorem 2 fails for the BSSC.  Theorem 1's
cardinality statement can still describe the BSSC's Markov-constrained class
with \(|U'|,|V'|\leq 2\), but neither theorem certifies or refutes a Markov
optimizer for the BSSC.  This prunes a tempting but invalid direct port.

## Reproducibility-repository audit

The 20 August paper links
[`yanxiaoliu-mike/Suboptimality_Marton`](https://github.com/yanxiaoliu-mike/Suboptimality_Marton).
The audit pinned the one-commit Git tree
[`cc33e854cb1c5e99cb18fe500f60a529fce136f8`](https://github.com/yanxiaoliu-mike/Suboptimality_Marton/tree/cc33e854cb1c5e99cb18fe500f60a529fce136f8).
Tracked wrappers and Python/C++ verifier sources were inspected before any
execution.  `replay_evidence.json` records the environment, commands, and
machine-readable results.

After installing `mpmath==1.4.1`, `numpy==2.5.2`, and `gmpy2==2.3.1` in a
disposable path, the following individual checks passed:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 src/portable/verify_saved_certificate_manifest.py

PYTHONPATH=/tmp/marton-repro-deps-wemcba PYTHONDONTWRITEBYTECODE=1 \
  python3 src/portable/quick_audit.py

PYTHONPATH=/tmp/marton-repro-deps-wemcba PYTHONDONTWRITEBYTECODE=1 \
  python3 src/certificate/verify_fixed_input_bundle.py

bash scripts/run_lift_mpfr.sh
```

The saved-bundle audit reported 8 valid component hashes, all 81 deterministic
maps plus the two one-sided branches, and 4,729,704 processed boxes.  The
fixed-input verifier recomputed the directed one-letter upper bound and
two-letter lower bound with positive gap
\(2.827537944275559805\ldots\times10^{-6}\) nats.  The 320-bit lift verifier
reported

\[
M_{T^{\otimes2}}-2M_T
\in[1.882125632718549\times10^{-6},
1.8821256327554852\times10^{-6}]\ \text{nats}.
\]

### Exact replay caveat

At the pinned commit, `SHA256SUMS` lists `.gitignore`, `paper/main.tex`, and
`paper/paper.pdf`, but those three paths are absent from the Git tree.  Running

```bash
sha256sum -c SHA256SUMS
```

in a clean detached checkout therefore exits nonzero for exactly those three
missing paths; every present path reports `OK`.  The README and `PROVENANCE.md`
describe the absent paper files as part of the package.  Moreover,
`scripts/run_quick.sh` begins by running
`src/portable/check_paper_transcription.py`, which opens the absent
`paper/main.tex`.  Consequently the advertised top-level path to
`ALL QUICK CHECKS PASSED` cannot complete from the pinned Git tree as checked
in.  The individual checks above avoid only that unavailable transcription
step.

There is one additional, benign replay mutation: `scripts/run_lift_mpfr.sh`
overwrites `results/unconstrained_lift_mpfr.txt`.  The local run recorded MPFR
4.2.1 whereas the committed transcript records MPFR 4.2.2, so rerunning the
manifest in that dirty replay checkout also flags the overwritten transcript.

These omissions and transcript drift limit whole-repository replay.  They are
kept separate from theorem validity: the numerical replays corroborate stated
numbers, while the analytic theorems remain attributed external results and
are not independently proved by this contribution.

## Deterministic local verification

From this contribution directory, run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_audit.py
```

The networkless standard-library checker verifies the exact BSSC matrices,
row stochasticity, skew reflection, presence of transition zeros, the
machine-readable superadditivity/limit declarations and the common-term
minimum inequality on an exact-rational regression grid, the stationary
quadratic and its sign pattern, the 100-digit evaluation of the exact RTD
closed form, both 33-digit displays, source
identifiers/versions/timestamps/PDF digests, theorem-number and input-alphabet
declarations, pinned Git commit, positive replay intervals, map/branch
coverage, and the exact missing-file caveat.  It does not prove Marton's
coding theorem, the classical binary-input one-letter evaluation, or either
August 2026 paper.

## Provenance and limitations

- Marton's coding theorem and the Geng--Jog--Nair--Wang binary-input evaluation
  are external premises; the latter is linked in the canonical problem
  statement as [arXiv:1001.1468](https://arxiv.org/abs/1001.1468).
- The two August 2026 theorem statements, their examples, and their numerical
  constructions belong to the cited authors.  This contribution supplies the
  super-symbol normalization proof, exact BSSC threshold specialization,
  scope/non-applicability audit, and reproducibility audit.
- No BSSC two-letter witness, new numerical BSSC lower bound, binary-input
  nonadditivity theorem, or capacity converse is claimed.
- The external PDF SHA-256 values authenticate the exact bytes audited here;
  the PDFs are not copied into this contribution.
