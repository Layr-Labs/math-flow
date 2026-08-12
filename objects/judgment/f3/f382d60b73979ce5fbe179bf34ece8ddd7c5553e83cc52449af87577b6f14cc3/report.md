# Mathematical judgment

## Executive assessment

The subject contribution does **not** determine \(D(77)\) and does not improve the certified interval

\[
152\le D(77)\le 154.
\]

Its principal mathematical value is instead a symmetry-reduced, reproducible exact model for searching for a \(154\)-point configuration in the specified **rct4** subclass. Static inspection of the supplied code and argument supports the claimed soundness and completeness of that model **within the rct4 class**.

The elementary half-turn and quarter-turn lemmas are correct. The conclusion that a \(154\)-point half-turn-invariant configuration must be centered at \((38,38)\) is also correct. There are, however, two important scope qualifications:

1. The displayed lemma does not by itself prove that the rct4 subclass is the only rotationally symmetric route. General configurations invariant only under the centered half-turn form a strictly broader class, as the contribution itself acknowledges later.
2. If “rotational symmetry” means rotation about an arbitrary center, rather than only a rotation in the dihedral symmetry group of the square grid, a short additional lattice-rotation classification lemma is missing from the written proof.

The reported solver timeouts establish no satisfiability or unsatisfiability result. They are not accompanied by committed logs and are expressly reported as `UNKNOWN` or timeout outcomes. They therefore have no implication for \(D(77)\) or even for the satisfiability of the rct4 instance.

---

## Finding 1: Odd no-three-in-line sets cannot have nontrivial half-turn symmetry

**Claim key:** `no-three-in-line/odd-cardinality-half-turn-obstruction`

**Status:** Accepted.

### Precise claim

Let \(S\) be a finite no-three-in-line set invariant under the half-turn

\[
p\longmapsto 2z-p
\]

about a point \(z\). If \(|S|\) is odd, then \(|S|\le 1\). In particular, a \(153\)-point no-three-in-line set cannot have half-turn symmetry about any center.

### Decisive reasoning

A half-turn is an involution whose only fixed point is its center \(z\). Its action on \(S\) partitions \(S\) into two-element orbits, together possibly with the singleton orbit \(\{z\}\). Odd cardinality therefore forces \(z\in S\).

If \(p\in S\) and \(p\ne z\), invariance also puts \(2z-p\) in \(S\). The three distinct points

\[
p,\quad z,\quad 2z-p
\]

are collinear, with \(z\) their midpoint. This contradicts the no-three-in-line condition. Thus no other point can occur and \(S=\{z\}\).

This proof is complete and does not require \(z\) to have been assumed a grid point: odd cardinality forces the fixed point \(z\) itself to belong to \(S\), and hence to the grid.

---

## Finding 2: Quarter-turn symmetry is impossible at cardinalities \(153\) and \(154\)

**Claim key:** `no-three-in-line/quarter-turn-cardinality-obstruction`

**Status:** Accepted.

### Precise claim

A no-three-in-line set invariant under a quarter-turn has cardinality either divisible by \(4\) or equal to \(1\). Consequently, neither a \(153\)-point nor a \(154\)-point no-three-in-line set can have quarter-turn symmetry.

### Decisive reasoning

For a quarter-turn about \(z\), every noncentral orbit has size \(4\). An orbit of size \(2\) would be fixed by the square of the quarter-turn, namely the half-turn about \(z\), but that half-turn fixes only \(z\).

If \(z\notin S\), \(S\) is a disjoint union of four-element orbits and therefore has cardinality divisible by \(4\). If \(z\in S\), quarter-turn invariance also gives half-turn invariance; the midpoint argument from the previous finding shows that a no-three-in-line set containing \(z\) can then contain no other point. Hence the only central case has cardinality \(1\).

Since

\[
153\equiv 1\pmod 4,\qquad 154\equiv 2\pmod 4,
\]

a \(153\)-point invariant set would have to contain the center but could not contain its other \(152\) points, while \(154\) is incompatible with the orbit sizes outright.

---

## Finding 3: A half-turn symmetry of a \(154\)-point set must be centered at \((38,38)\)

**Claim key:** `no-three-in-line/d77-154-half-turn-center`

**Status:** Accepted.

### Precise claim

If \(S\subseteq G_{77}\) is no-three-in-line, has \(154\) points, and is invariant under a half-turn, then that half-turn is about the grid center \((38,38)\), and the center is unoccupied.

### Decisive reasoning

Every horizontal row contains at most two points. There are \(77\) rows and \(|S|=154\), so every row contains exactly two points. Applying the same argument to vertical columns shows that every column contains exactly two points.

Thus the coordinate extrema of \(S\) are

\[
\min x=\min y=0,\qquad \max x=\max y=76.
\]

A half-turn about \(z=(z_x,z_y)\) sends the \(x\)-coordinate interval \([0,76]\) to \([2z_x-76,2z_x]\). Invariance of the set, and hence of its coordinate extrema, forces

\[
2z_x-76=0,\qquad 2z_x=76,
\]

so \(z_x=38\). Similarly \(z_y=38\).

The center cannot be occupied: if \((38,38)\in S\), any noncentral point and its half-turn image would form a forbidden collinear triple with the center.

---

## Finding 4: The broader “only rotational route” wording is not fully established as written

**Claim key:** `no-three-in-line/d77-rotational-symmetry-classification-at-153-154`

**Status:** Qualified; the central conclusion is plausible and repairable, but the supplied argument overstates what the displayed lemma proves.

### Missing classification step

The contribution defines half-turns and quarter-turns about arbitrary centers and then says that the only rotational symmetry available above \(152\) points is a centered half-turn at cardinality \(154\). The written lemma analyzes rotations of orders \(2\) and \(4\), but it does not explicitly rule out rotations of other orders preserving a finite subset of the integer lattice.

A short missing lemma would close this gap: a rotation preserving a finite set of at least three noncollinear integer points has a rational rotation matrix, because it sends two independent integer difference vectors to integer difference vectors. Since the rotation has finite order, rationality of both sine and cosine restricts it to the usual orders \(1,2,\) or \(4\). The present contribution does not state or prove this classification.

If “rotational symmetry” was intended to mean only rotations in the dihedral symmetry group of the square \(G_{77}\), then this gap is terminological rather than substantive. The text’s repeated reference to rotations about “any center point \(z\) of the plane” makes the broader interpretation natural, however, so the missing step should be recorded.

### rct4 is not the whole half-turn class

More importantly, the rct4 conditions impose considerably more than centered half-turn invariance:

- the anti-diagonal is empty;
- almost all selected points occur in complete quarter-turn orbits;
- the only departure from full quarter-turn invariance is one selected pair on the main diagonal.

A general set invariant under the centered half-turn need not satisfy any of these additional conditions. Thus the introductory description of the package as “the one viable rotational route” and the suggestion that the symmetry lemma proves it is the only such route are too broad if they refer to the rct4 model itself.

The contribution later correctly acknowledges this limitation:

> “General half-turn (rot2) configurations satisfy a weaker symmetry … a rot2-general model … is not included.”

That limitation is mathematically decisive. The correct scope is:

> Centered half-turn symmetry is the only possible nontrivial rotational symmetry type at cardinality \(154\), while rct4 is one strict, historically successful subclass of centered half-turn configurations.

There is no contradiction in the underlying mathematics once the statement is narrowed this way, but the introductory wording and the limitations section are not fully consistent.

---

## Finding 5: The rct4 model is an exact encoding of the stated subclass

**Claim key:** `no-three-in-line/d77-rct4-154-model-equivalence`

**Status:** Accepted with high confidence from the supplied argument and code.

### Precise claim

Feasible assignments of the \(n=77\) model correspond exactly to \(154\)-point no-three-in-line sets satisfying the stated rct4 pattern:

1. the anti-diagonal is empty;
2. off the two diagonals, occupied cells are unions of complete quarter-turn orbits;
3. exactly one half-turn pair on the main diagonal is occupied.

### Orbit structure and cardinality

For odd \(n\), let

\[
\rho(i,j)=(j,n-1-i).
\]

At \(n=77\), the grid center is \((38,38)\).

After removing the main and anti-diagonals, there are

\[
77^2-(2\cdot 77-1)=5776
\]

cells. These fall into quarter-turn orbits of size \(4\), giving

\[
5776/4=1444
\]

off-diagonal orbit variables.

The noncentral main-diagonal points form \(38\) half-turn pairs, giving \(38\) diagonal-pair variables. The model imposes

\[
\sum y_{\mathrm{off}}=38,\qquad \sum y_{\mathrm{diag}}=1.
\]

Therefore every feasible assignment selects

\[
4\cdot 38+2=154
\]

grid points.

The implementation treats the center correctly: it belongs to the anti-diagonal and is skipped before main-diagonal variables are assigned.

### Completeness of the line enumeration

The code enumerates primitive directions \((dx,dy)\) with canonical sign and

\[
\max(|dx|,|dy|)\le \frac{n-1}{2}.
\]

Any lattice line containing three grid points has a primitive step for which two steps fit inside the grid, so both coordinate increments satisfy this bound. Vertical and horizontal directions are included separately.

For each direction, a line is started only at a point whose predecessor is outside the grid. Thus each maximal grid line with at least three lattice points is enumerated once.

### Correct translation to orbit variables

For every enumerated line, the coefficient of an orbit variable is the number of cells from that orbit lying on the line. The inequality

\[
\sum_v c_v y_v\le 2
\]

therefore says exactly that the resulting point set contains at most two selected cells on that line.

Any collinear triple of grid points lies on one of the enumerated maximal lattice lines. Consequently:

- every feasible assignment yields a no-three-in-line set;
- every rct4-pattern \(154\)-point no-three-in-line set induces a feasible assignment.

Discarding lines whose total possible coefficient sum is at most \(2\) is harmless because their inequalities are tautological. Deduplicating identical weighted inequalities is also harmless.

### CNF export

The CNF translation of a weighted at-most-two constraint is logically correct:

- a variable of coefficient at least \(3\) is forced false;
- two coefficient-\(2\) variables cannot both be true;
- a coefficient-\(2\) variable cannot coexist with a coefficient-\(1\) variable;
- among coefficient-\(1\) variables, every triple is forbidden.

Together these clauses are equivalent to the weighted bound. The exact-cardinality constraints are delegated to PySAT’s standard cardinality encoder.

### Computational count

The reported \(n=77\) statistics,

- \(1444\) off-orbit variables,
- \(38\) diagonal-pair variables,
- \(388{,}148\) deduplicated line constraints,

are deterministically regenerated by the supplied program and compared byte-for-byte with `results.json`. The variable counts also follow directly from the orbit calculation above. The precise line-constraint count remains a computational census rather than a hand-derived theorem, but the code for producing it is explicit and uses exact integer arithmetic.

---

## Finding 6: The five supplied calibration certificates support implementation validity only at their listed sizes

**Claim key:** `no-three-in-line/rct4-model-calibration-certificates`

**Status:** Accepted within the exact scope of the five committed lines.

The program checks the supplied certificates at

\[
n=41,47,57,65,69.
\]

For each line it:

1. decodes two points per row;
2. checks distinctness and grid membership;
3. checks every point triple by an exact determinant;
4. checks the empty anti-diagonal and complete orbit structure;
5. checks the induced assignment against all generated model constraints.

Static inspection shows that these are meaningful exact checks. The certificate payload itself forces \(2n\) decoded points, so the orbit-count check, together with distinctness, also ensures that the single selected diagonal variable represents its full two-point pair in these calibration cases.

These examples provide useful regression tests and show that the implementation accepts five genuine-looking instances of the intended class. They do not independently prove the historical claim that every relevant odd-size record in an entire range belongs to this class; only the five committed certificates are directly checked here. The supplied hashes establish file identity, not external provenance or discovery priority.

---

## Finding 7: The bounded searches prove neither satisfiability nor unsatisfiability

**Claim key:** `no-three-in-line/d77-rct4-154-satisfiability`

**Status:** Open; no mathematical conclusion supplied.

No solver found a configuration within the reported budgets, but no solver returned a certified `INFEASIBLE` result. The contribution correctly labels the CP-SAT outcomes as `UNKNOWN` and the SAT outcomes as timeouts.

Moreover, the same pipeline reportedly failed under comparable budgets at \(n=41\) and \(n=47\), where committed certificates demonstrate satisfiability. This is decisive evidence that the timeout behavior has essentially no negative force for the \(n=77\) instance.

The search table is also not part of the deterministic `results.json`, and no solver logs, proof traces, or exact CaDiCaL invocation are committed. Thus the table can be treated as an honestly scoped run report, but not as an independently certified computational result.

In particular, it establishes none of the following:

- that the rct4 \(n=77\) instance is satisfiable;
- that the rct4 \(n=77\) instance is unsatisfiable;
- that no centered half-turn \(154\)-point configuration exists;
- that \(D(77)<154\).

The private-channel “breakthrough report” likewise carries no mathematical weight because no coordinate certificate, proof, solver output, or even definite claimed value is supplied.

---

## Finding 8: The exact value and certified interval remain unchanged

**Claim key:** `no-three-in-line/d77-exact-value`

**Status:** Unresolved.

The subject transaction provides no \(153\)- or \(154\)-point coordinate certificate and no global upper-bound improvement. It is compatible with each remaining possibility

\[
D(77)\in\{152,153,154\}.
\]

Accordingly, the supplied evidence continues to support only

\[
\boxed{152\le D(77)\le 154}.
\]

The rct4 model is a useful restricted search artifact, but failure or success within that class would have the following limited implications:

- a feasible assignment would prove \(D(77)=154\);
- a proof that the rct4 instance is infeasible would rule out only the rct4 subclass, not all \(154\)-point sets;
- even ruling out all centered half-turn configurations would leave reflection-symmetric and asymmetric \(154\)-point possibilities unless further arguments were supplied.

---

## Scope and attribution

The new mathematical content consists of the symmetry observations, the \(n=77\) rct4 model implementation, its validation machinery, and the bounded search report attributed to Robert Raynor and the disclosed AI research agent. The underlying rct4 class and symmetry-reduction method are attributed in the contribution to Thomas
