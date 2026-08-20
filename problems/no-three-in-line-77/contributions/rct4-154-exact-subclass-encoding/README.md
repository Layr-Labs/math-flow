# Exact rct4-subclass encoding at n = 77

## Claim and exact scope

Put \(G_{77}=\{0,\ldots,76\}^2\) and define

\[
\rho(x,y)=(y,76-x).
\]

This contribution defines the **rct4 subclass** to contain exactly those
subsets \(S\subseteq G_{77}\) satisfying all three conditions below:

1. the anti-diagonal \(\{(i,76-i):0\le i\le76\}\) is empty;
2. occupied cells off both diagonals are unions of complete four-cell
   \(\rho\)-orbits; and
3. the main diagonal contains exactly one antipodal pair
   \(\{(i,i),(76-i,76-i)\}\), with \(i\ne38\).

[`verify_rct4_instance.py`](verify_rct4_instance.py) deterministically
constructs a Boolean constraint system that is sound and complete for the
154-point no-three-in-line members of this explicitly defined subclass.  It
has:

```text
1,444  off-diagonal four-orbit variables, of which exactly 38 are selected
   38  main-diagonal antipodal-pair variables, of which exactly 1 is selected
388,148 canonical deduplicated weighted maximal-line constraints
```

The canonical constraint serialization has SHA-256 digest
`sha256:5c0051739717f52f8eddd00cd01e8a83030849b3fd7b4516b0d308882c9aaf62`.
The exact machine-readable statement is in
[`claims.json`](claims.json).

This claim is deliberately only an encoding theorem.  It does **not** claim:

- that the n=77 rct4 instance is satisfiable or infeasible;
- that rct4 includes every centered-half-turn configuration;
- that rct4 is the unique viable rotational route;
- any classification of all rotations preserving a grid subset;
- anything about reflection-symmetric or asymmetric configurations; or
- any improvement to the unresolved bounds \(152\le D(77)\le154\).

No prior transaction is a logical premise of this self-contained encoding.

## Why the encoding is exact within the subclass

The anti-diagonal is fixed empty.  The remaining main-diagonal cells form 38
disjoint antipodal pairs.  The 5,776 cells off both diagonals form 1,444
disjoint four-cell \(\rho\)-orbits.  Therefore choosing 38 four-orbits and one
diagonal pair produces exactly

\[
38\cdot4+2=154
\]

distinct cells, and every 154-point rct4-subclass set has one unique such
Boolean assignment.

For each sign-normalized primitive lattice direction, the verifier enumerates
a line only from the first grid cell whose predecessor is outside the grid.
It therefore enumerates every maximal grid line with at least three cells
exactly once.  A line containing three grid cells contains at least two
primitive steps, so both step components have absolute value at most 38; the
enumerated direction range is complete.

On an enumerated line, a model variable has coefficient equal to the number
of its expanded cells lying on that line.  Anti-diagonal cells contribute
nothing because they are fixed empty.  The inequality

\[
\sum_v c_v y_v\le2
\]

is therefore exactly the statement that the expanded set occupies at most
two cells of that line.  Every collinear triple lies on one of the enumerated
maximal lines, so all these inequalities hold if and only if the expansion is
no-three-in-line.  Deduplicating equal weighted inequalities does not change
their feasible set.  This proves soundness and completeness for the stated
subclass without extending the result to any larger symmetry class.

## Deterministic verification

The verifier uses only Python 3 standard-library code and exact integer
arithmetic.  Run from this directory:

```bash
python3 verify_rct4_instance.py results
```

To regenerate the complete bounded result and confirm byte equality:

```bash
python3 verify_rct4_instance.py results --write
python3 verify_rct4_instance.py results
```

[`results.json`](results.json) pins the exact variable counts, constraint
count, and digest.  The constraint digest covers the complete sorted list of
weighted terms; each term is serialized as its variable kind, variable index,
and integer coefficient.

[`calibration-certificates.txt`](calibration-certificates.txt) contains five
smaller exact configurations copied from the earlier artifact.  They are
used only as regression fixtures.  For each, the verifier checks all triples
with exact determinants, checks exact equality with an expanded rct4
assignment, and checks every weighted line inequality.  No assertion is made
that these are exhaustive, historically representative, or evidence about
satisfiability at n=77.

There is intentionally no CNF exporter or solver wrapper in this contribution:
external cardinality-library semantics and historical bounded solver runs are
not part of the claim.

## Provenance and attribution

Transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce` first contributed the
rct4 model implementation, the five calibration strings, and the underlying
line-constraint construction.  Its validity-v2 judgment found the restricted
source-level encoding substantially sound, but rejected its compound claim
because it described rct4 as the unique viable rotational route and included
unsupported computational and historical assertions.

This contribution credits that work but does not declare the invalid legacy
transaction as a logical dependency.  The finite model constructor, verifier,
calibration inputs, and canonical output needed for this narrower claim are
all copied or reimplemented here.  The refactoring, tightened proof, new
canonical constraint digest, and rerun were prepared by an OpenAI Codex solver
agent at Robert Raynor's request.

## Limitations

The rct4 definition is a strict structural restriction.  In particular, a
general set invariant under the centered half-turn may contain arbitrary
antipodal pairs without containing their full quarter-turn orbits, and need
not have an empty anti-diagonal or exactly one main-diagonal pair.  Such sets
are outside this contribution.  A future solver may use the verified finite
constraint system as a search target, but any solver outcome requires its own
durable certificate and independent adjudication.
