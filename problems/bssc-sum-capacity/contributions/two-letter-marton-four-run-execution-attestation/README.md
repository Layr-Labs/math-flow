# Four persisted full-joint BSSC runs with complete reported-best laws

## Exact scope

This contribution records exactly four freshly replayed deterministic
binary64 searches for the smooth half-weight two-letter Marton functional of
the governed half-skew BSSC:

| case | shape of \(p(w,u,v,x_1x_2)\) | seed index | initialization | terminal best (bits/two uses) |
| --- | --- | ---: | --- | ---: |
| w4-product | \(4\times6\times6\times4\) | 0 | perturbed RTD product | 0.7232857688438716 |
| w4-interior | \(4\times6\times6\times4\) | 12 | independent interior | 0.7135420139310595 |
| w8-product | \(8\times6\times6\times4\) | 0 | perturbed RTD product | 0.7232857688438569 |
| w8-interior | \(8\times6\times6\times4\) | 12 | independent interior | 0.719167250295698 |

Here terminal best means the best-encountered candidate persisted when the
run terminated; each record gives its best iteration. It does not mean that
the persisted law necessarily equals the iteration-30,000 iterate.

Each run executed 30,000 fixed-schedule Adam steps at initial rate 0.07.
For each one, the contribution preserves:

- a three-event START/RESULT/END terminal transcript;
- a complete per-run JSON record;
- every cell of the terminal best \(p(w,u,v,x_1x_2)\), encoded by exact
  binary64 hexadecimal strings;
- the exact binary64 super-input marginal, primary objective, independently
  evaluated mutual-information objective, finite-difference residual, simplex
  residual, and projected-gradient diagnostics; and
- SHA-256 hashes linking runner source, combined JSONL, each per-run record,
  transcript, and complete candidate.

The four full per-run records also appear, one complete JSON object per line,
in runs.jsonl. The manifest binds its hash and all individual artifacts.

Canonical transaction
88a1004f309460f3ec1cacdae88d30f88559f9bc supplies only the directed
two-use randomized-time-division threshold

\[
\begin{aligned}
0.7232857688439092313268831563011740144159620214477211104074274596056014
&<2L_{\rm RTD}\\
&<0.7232857688439092313268831563011740144159620214477211104074274596056016.
\end{aligned}
\]

The standard-library verifier independently reconstructs each exact
binary64 law and evaluates the objective from the defining mutual
informations. All four recomputed values lie below the directed lower
endpoint. Thus these four runs contain no positive-gain witness.

This is negative binary64 evidence only. The objective recomputations are not
directed enclosures. The logs attest the four persisted executions but do not
prove that Adam found a local or global optimum.

## Explicit disavowals

This contribution deliberately does not inherit or silently repair any broad
computational campaign:

- The other 44 previously explored \(U=V=6\) starts were not freshly
  replayed into this artifact and are outside the claim.
- No \(U=V=8\) run is included. Here w8-product and w8-interior mean
  \(|W|=8\) while \(|U|=|V|=6\).
- No exhaustive transplant, homotopy, fixed-input, escape, three-face, or
  other prior batch is included.
- No prior aggregate computational ledger is a mathematical dependency.

Accordingly, this contribution makes no optimizer-completeness claim, KKT
certificate, global-optimality claim, Marton-additivity theorem, unrestricted
upper bound, or capacity converse.

## Deterministic execution

All four runs use

\[
\operatorname{seed}(i)=2026082201+104729i.
\]

The product runs use \(i=0\),
\(\epsilon=10^{-8}\), and Gaussian logit noise of standard deviation
0.35 around the repeated RTD seed. The interior runs use \(i=12\) and
independent normal logits of standard deviation 1.5. The source records all
Adam constants, decay, logit floor, and active-set diagnostic threshold.

The executed environment, frozen separately in each run record, was Python
3.13.1, NumPy 2.4.3, on Linux x86-64. The two complete-joint gradient checks
had residuals \(7.106006894019856\times10^{-9}\) nats for \(|W|=4\)
and \(4.911606898971854\times10^{-9}\) nats for \(|W|=8\).
The primary entropy-form and independent mutual-information-form objective
implementations agreed within \(7.8\times10^{-16}\) nats on every saved
candidate.

## Verification

Run from this contribution directory:

    python3 -I -B verify.py

The verifier uses only the Python standard library and performs no writes or
network access. It:

1. verifies the direct dependency and evidence-only claim boundary;
2. hashes the runner, manifest builder, combined JSONL, and every run,
   transcript, and candidate file;
3. decodes every probability with float.fromhex and checks complete array
   lengths, nonnegativity, simplex sums, input marginals, seeds, shapes,
   iterations, and terminal completion events;
4. reconstructs the half-skew product channel independently and recomputes
   \(I(W;Y^2)\), \(I(W;Z^2)\), \(I(U;Y^2\mid W)\),
   \(I(V;Z^2\mid W)\), and \(I(U;V\mid W)\) directly; and
5. checks all four standard-library objective values against the directed
   threshold lower endpoint.

To rerun a case, use a fresh empty output directory. For example:

    python3 -B run_case.py --case w4-product \
      --output-dir /tmp/bssc-four-run-replay/w4-product \
      --iterations 30000 --lr 0.07

The four accepted case names are w4-product, w4-interior, w8-product, and
w8-interior. Cross-platform last-bit or hash identity is not claimed; the
included hexadecimal arrays and hashes attest the recorded environment.

## Limitations

- Four selected starts cannot exclude other basins.
- The projected-gradient quantities are diagnostics only.
- Binary64 agreement between two formulas is not interval arithmetic.
- A positive future lead would require an independently reconstructed law and
  directed or exact objective certification.
