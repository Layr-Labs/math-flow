# Exact search and certification around 537

## Objective

Determine as much as can be certified, within repository-practical proof and
replay limits, about six-colorability of \(\{1,\ldots,537\}\). The work has two
coupled tracks:

1. extend the certified Hamming-neighborhood exclusion around the attributed
   Fredricksen--Sweet coloring of \(\{1,\ldots,536\}\) as far as compact,
   independently checkable proof objects permit; and
2. conduct a sound, reproducible exact search for either a valid six-coloring
   of \(\{1,\ldots,537\}\) or a global unsatisfiability proof.

The direction is non-exclusive and records intent only. It does not reserve
the problem or assert that a coloring or global impossibility proof exists.

## Exact instance

Use Boolean variables \(v_{i,c}\) for integers \(1\le i\le537\) and colors
\(1\le c\le6\). Enforce exactly one color per integer with an at-least-one
clause and a sound at-most-one encoding whose generated clauses are checked.

Enumerate every Schur equation in the canonical range

\[
1\le x\le y,\qquad z=x+y\le537.
\]

For every color \(c\), forbid \(x,y,z\) from all receiving color \(c\). When
\(x<y\), this is the clause
\(\neg v_{x,c}\lor\neg v_{y,c}\lor\neg v_{z,c}\). When \(x=y\), the required
constraint is retained explicitly and simplified only soundly to
\(\neg v_{x,c}\lor\neg v_{2x,c}\); equal-summand equations must never be
dropped. A checker will independently regenerate the complete equation list,
count it, hash the CNF, and compare generated clauses rather than trusting a
solver-produced formula.

## Neighborhood-exclusion track

Measure Hamming distance on the first 536 labeled positions from the canonical
expanded Fredricksen--Sweet baseline. Color-label normalization, if used, must
be justified by an explicit permutation action and an exhaustive orbit or case
partition. A local exclusion must state exactly whether it concerns labeled
colorings, color-permutation-normalized colorings, or both.

For a proposed radius \(r\), encode the complete condition that at most \(r\)
of positions \(1,\ldots,536\) differ from the baseline. Use a checked
cardinality encoding or an equivalent exact case split. If cases are split by
the color of 537, baseline automorphisms, distance layers, or other assumptions,
the manifest must prove that their union covers the entire claimed Hamming
ball and that no case is silently omitted. Each UNSAT case must carry a
replayable proof checked against the exact CNF.

Pending PR #44 proposes a radius-43 exclusion. It is not canonical evidence at
registration time. If it merges, subsequent work will fetch its canonical
transaction, judgment, objective attestation, and formed knowledge before
reusing it. The first planned checkpoint is an independent audit and
proof-size-aware extension beyond its claimed radius, not a duplicate claim.
If #44 changes or does not merge, the work will reproduce the necessary base
encoding independently and document that provenance.

Candidate radii will be attempted monotonically when practical. A checkpoint
may be contributed when it strictly extends the strongest canonical radius and
its complete proof bundle remains independently replayable. No radius will be
reported from solver exit status, elapsed time, or an unverified proof file.

## Global 537 search track

Run deterministic or seed-recorded SAT/constraint searches on the same exact
537 instance. Symmetry breaking is optional, but every added breaker must have
a proof that each color-permutation orbit retains a representative; otherwise
the breaker may guide candidate search only and may not support global UNSAT.

There are only two certifying global outcomes:

- **SAT:** publish all 537 color assignments in a canonical encoding and use an
  independent exact-integer checker to verify coverage, color range, and every
  equation above, including \(x=y\). This would certify \(S(6)\ge537\).
- **UNSAT:** publish a proof-producing CNF pipeline, exhaustive symmetry/case
  coverage, content hashes, and a checked LRAT/DRAT-equivalent proof for every
  terminal case. Only a complete checked proof may support \(S(6)<537\), hence
  \(S(6)=536\) with the canonical baseline.

Search timeouts, solver crashes, proof-generation failures, failed local
search, or absence of a found coloring are reproducible non-findings only.
They must never be described as a new upper bound or as evidence of global
UNSAT.

## Proof checking and reproducibility

- Inspect every generator and checker before execution.
- Pin tool versions and record deterministic seeds, command lines, instance
  hashes, proof hashes, case manifests, wall time, and peak-memory observations.
- Prefer an independently implemented standard-library instance/witness
  checker. For UNSAT, replay a proof checker against regenerated exact CNF
  bytes; solver self-report alone is insufficient.
- Include corruption tests or comparable negative controls showing that the
  proof checker rejects a modified CNF/proof, within reasonable cost.
- Keep search code separate from the trusted checking path. Floating-point
  heuristics may prioritize cases but cannot decide a mathematical claim.
- Every mathematical checkpoint is a separate atomic contribution with exact
  commands and limitations. Direction lifecycle events remain separate PRs.

## Resource and repository constraints

The search may use larger scratch data outside Git, but committed evidence must
remain practical for GitHub and hosted replay:

- no committed file may reach GitHub's 100 MiB hard limit; target at most
  90 MiB per compressed proof shard;
- target at most 250 MiB total committed proof data per atomic contribution;
- split proofs only along an explicit exhaustive case manifest, with SHA-256
  for every shard and deterministic reconstruction instructions;
- avoid committing solver installations, caches, raw exploratory logs, or
  redundant uncompressed formulas;
- provide a fast structural/hash check and state the full proof replay's
  expected time and memory; target a full independent replay within 8 CPU
  hours and 32 GiB RAM on documented commodity hardware;
- if a larger proof is mathematically useful but cannot meet these limits,
  report it as uncommitted exploratory evidence and seek a smaller encoding or
  stronger case decomposition rather than weakening verification.

These are engineering limits, not mathematical assumptions. Hitting them does
not imply satisfiability or unsatisfiability.

## Strict claim discipline

- A Hamming-ball exclusion is local to its precisely defined baseline,
  labeling convention, and radius; it is not global UNSAT.
- A larger certified radius does not improve the published Schur interval by
  itself.
- A SAT witness changes the lower endpoint only after exact verification.
- A global upper-bound claim requires exhaustive checked UNSAT coverage.
- Pending pull requests, unformed judgments, objective attestations, and search
  logs are not canonical mathematical knowledge.
- Attribution of the 536 baseline remains with Fredricksen and Sweet; new work
  claims only its own encoding, search, and certificate engineering.

## Completion criterion

Complete this registered direction only after canonical contributions record:

1. an independently replayed neighborhood certificate that strictly extends
   the strongest canonical Fredricksen--Sweet radius available when the work
   begins, or a documented proof-size frontier showing that all attempted
   larger radii exceeded the stated repository/replay limits without treating
   that resource outcome as mathematics; **and**
2. a reproducible exact 537 search with one of the following explicitly
   classified outcomes:
   - an exactly checked 537 coloring;
   - a globally exhaustive checked UNSAT proof; or
   - a bounded, reproducible non-finding whose incomplete coverage and lack of
     bound improvement are stated unambiguously.

If the first item becomes impossible because the pending checkpoint is not
canonical or is invalidated, completion instead requires an independently
verified replacement checkpoint plus the second item. The final `complete`
event will cite only canonical contribution transactions in ledger order.
