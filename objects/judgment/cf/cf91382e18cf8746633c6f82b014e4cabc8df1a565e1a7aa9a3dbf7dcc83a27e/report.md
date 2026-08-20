## `no-three-in-line-77/rct4-154-search-instance`

**Verdict: indeterminate**

The supplied source supports several important mathematical components, but the exact declared claim is not fully established. In particular, the asserted classification of all rotational symmetries has a material proof gap, and none of the large deterministic computations or reported solver runs has terminal execution evidence.

### 1. Symmetry lemma

#### Half-turn symmetry for odd cardinality

This part is correct.

A half-turn about \(z\) is an involution whose only fixed point is \(z\). Hence an invariant finite set of odd cardinality contains \(z\). If it also contains \(p\ne z\), it contains \(2z-p\), and the three distinct points
\[
p,\ z,\ 2z-p
\]
are collinear. Thus a no-three-in-line half-turn-invariant set of odd cardinality has at most one point. In particular, a 153-point set cannot have half-turn symmetry.

#### Quarter-turn symmetry

This part is also correct.

A quarter-turn has one possible fixed point, its center, and all other orbits have size four: a two-element orbit would be fixed by the half-turn square, whose unique fixed point is the center. Moreover, if the center and any other orbit were selected, half-turn invariance would produce a collinear triple through the center. Consequently a no-three-in-line quarter-turn-invariant set has either one point or cardinality divisible by four. Neither 153 nor 154 is possible.

#### Center of a half-turn-symmetric 154-point set

This part is correct for \(G_{77}\).

A 154-point no-three-in-line set has exactly two points in every one of the 77 rows, and likewise in every column. Its coordinate extrema are therefore \(0\) and \(76\) in both coordinates. A half-turn preserving the set must interchange the minimum and maximum coordinate values, forcing its center to be
\[
(38,38).
\]
The center cannot be occupied in a nontrivial half-turn-invariant no-three-in-line set.

#### Gap in the claimed classification of all rotations

The conclusion

> “the only rotational symmetry available above 152 points is … a half-turn about \((38,38)\)”

does **not follow from the supplied lemma**. The argument only analyzes rotations of orders two and four. It does not exclude rotations of order three, five, six, or other finite orders, nor does it prove that every rotational symmetry of a finite noncollinear subset of the integer lattice must have order two or four.

The desired conclusion is plausibly recoverable using an additional lattice/crystallographic argument—for example, showing that a rotation preserving a noncollinear finite integer set has a rational matrix and finite order, then excluding all orders except \(1,2,4\). But that argument is not supplied and cannot be inserted by the auditor. Therefore the assertions that this is the “only” rotational route and that a hypothetical 153-point set has “no rotational symmetry at all” remain unproved in the submitted record.

### 2. Definition and static structure of the rct4 model

The structural encoding is, on static inspection, mathematically coherent.

For odd \(n\), with
\[
\rho(i,j)=(j,n-1-i),
\]
the code:

- fixes the anti-diagonal empty;
- represents each off-diagonal \(\rho\)-orbit by one Boolean;
- represents each main-diagonal half-turn pair by one Boolean;
- chooses \((n-1)/2\) off-diagonal orbits and one diagonal pair.

At \(n=77\), the elementary variable counts are correct:

- \(77^2-77-76=5776\) cells lie off both diagonals;
- these form \(5776/4=1444\) four-element orbits;
- the 76 noncentral main-diagonal cells form 38 pairs;
- choosing 38 four-orbits and one pair gives
  \[
  4\cdot38+2=154.
  \]

The represented sets are half-turn invariant, have empty anti-diagonal, and satisfy the stated rct4 pattern.

### 3. Enumeration of collinearity constraints

The logic of `enumerate_lines` is sound on static inspection:

- directions are primitive;
- signs are normalized by taking positive \(x\)-step, with horizontal and vertical directions handled separately;
- a primitive direction component exceeding \((n-1)/2\) cannot support three grid points;
- only the first grid point on each maximal line is used;
- every line with at least three lattice points is enumerated.

Any three collinear integer grid points lie on one such primitive maximal line. Mapping cells on a line to orbit variables with multiplicities and imposing
\[
\sum_v w_v y_v\le 2
\]
therefore gives the correct no-three-in-line condition for represented configurations. Deduplicating identical inequalities does not affect soundness or completeness.

Thus the claimed **conditional correspondence** is established:

> If the generated constraints and cardinality equations are exactly those produced by the supplied code, feasible assignments correspond exactly to 154-point no-three-in-line configurations in the stated rct4 class.

This is only a class-restricted model. It does not cover general half-turn-symmetric configurations, reflection-symmetric configurations, or asymmetric configurations.

### 4. CNF and CP-SAT paths

The hand-written weighted-at-most-two CNF translation is logically correct for coefficients \(1,2,\ge3\):

- a coefficient at least three forces its variable false;
- two coefficient-two variables cannot both be true;
- a coefficient-two variable cannot coexist with a coefficient-one variable;
- no three coefficient-one variables can all be true.

However, the exported cardinality constraints depend on the external `python-sat` implementation of `CardEnc.equals`, whose generated clauses are neither included nor attested. Likewise, actual CP-SAT solving depends on external OR-Tools semantics and execution. The supplied source establishes the intended encoding, but not that any particular external-library invocation occurred or produced a specified file or result.

### 5. Exact numerical model statistics

The elementary counts \(1444\) off-orbit variables, \(38\) diagonal variables, and target size \(154\) are verified analytically.

The exact claim of **388,148 distinct line constraints**, and the analogous counts at calibration sizes, requires executing or independently reproducing the enumeration. `results.json` merely records claimed output; it is not itself a proof that the computation was performed correctly. No terminal objective attestation is present. Consequently those exact numerical counts remain unverified from the supplied record.

### 6. Five known-certificate checks

The checker’s algorithms are appropriate:

- it checks distinctness and grid membership;
- tests every triple with an exact integer determinant;
- verifies full off-diagonal orbit occupancy;
- checks the required orbit and diagonal-pair counts;
- evaluates every generated line inequality.

There is no evident logical defect in those checking routines. In particular, although `assignment_from_points` does not directly demand both cells of the chosen diagonal pair, the decoded certificate always has \(2n\) points; the required \((n-1)/2\) full four-orbits already account for \(2n-2\) points, so one diagonal index then necessarily accounts for both remaining cells.

Nevertheless, the factual assertion that all five supplied certificate lines pass the exhaustive checks is computational. There is no pinned terminal execution, and the exhaustive determinant and line-constraint results cannot be inferred merely from the booleans recorded in `results.json`. Therefore the five pass claims, their line hashes, and their exact constraint counts are unresolved.

The further historical assertion that these lines were reproduced from the stated external database is also not established by the supplied evidence; the full referenced download or a content-addressed snapshot is absent. This provenance issue is not needed for the mathematical model because the five encoded lines themselves are supplied.

### 7. Bounded search report

None of the reported CP-SAT or CaDiCaL runs is supported by logs, solver transcripts, generated CNF bytes, or terminal attestations.

There are also reproduction mismatches:

- the displayed \(n=77\) CP-SAT command uses four workers and a 3600-second budget, while the table reports two workers and at least 45 minutes;
- no CaDiCaL invocation command is supplied—only a CNF export command;
- seeds and exact stopping conditions are incomplete for several table entries.

Accordingly, the historical claims that these particular runs occurred and returned `UNKNOWN` or timed out are not verifiable from the packet. Their mathematical scope is correctly stated: even if the runs occurred, they would provide no nonexistence result.

### 8. Effect on \(D(77)\)

The model produces neither a 154-point certificate nor an infeasibility proof. The reported bounded searches, even if accepted, would not change any bound. Thus the contribution does not itself improve
\[
152\le D(77)\le154.
\]

The upper bound \(D(77)\le154\) is elementary. The baseline lower bound is part of the problem’s supplied premise; it is not independently re-established by this subject contribution.

### Required dependencies

- **`c5e8096d942d57228bb4fed00f7617fb6b43af9f`**: not required. Its local-rigidity result is motivation/provenance and is not used to establish the rct4 model or symmetry calculations.
- **`dfc0cc40d41105292a119840dcdbe6f22860cf43`**: not required for the model. The subject independently supplies its alphabet, decoder, and class-checking code. Its 152-point certificate is historical support for the already-given baseline interval, not a premise of the rct4 encoding.

### Objective evidence

No terminal objective attestations were supplied. Hence no command execution, generated CNF, exhaustive certificate verification, exact constraint count, or solver outcome is established by trusted execution evidence.

### Final assessment

The static rct4 encoding and the half-turn/quarter-turn sublemmas are substantially correct, but the exact declared claim cannot be accepted as valid because:

1. the claimed exhaustive classification of rotational symmetries omits all rotation orders other than two and four;
2. the exact line counts and five exhaustive certificate checks lack executed verification evidence;
3. the bounded search report is unsupported and not fully reproducible from the listed commands.

These are unresolved material obligations, so the conservative verdict is **indeterminate**, not valid.
