# Sound and complete Boolean encoding of the rct4 subclass

## Claim and exact scope

Let

\[
G_{77}=\{0,\ldots,76\}^2,
\qquad
\rho(x,y)=(y,76-x).
\]

Define the **rct4 subclass** to consist exactly of subsets
\(S\subseteq G_{77}\) for which:

1. the anti-diagonal \(A=\{(i,76-i):0\le i\le76\}\) is empty;
2. the occupied cells off both diagonals are unions of complete four-element
   \(\rho\)-orbits; and
3. the main-diagonal intersection is exactly one antipodal pair
   \(\{(i,i),(76-i,76-i)\}\), with \(0\le i<38\).

There is a sound and complete Boolean encoding of the 154-point
no-three-in-line members of this explicitly defined subclass:

- assign one Boolean variable to each four-element \(\rho\)-orbit off both
  diagonals and require exactly 38 of these variables to be one;
- assign one Boolean variable to each main-diagonal antipodal pair and require
  exactly one of these variables to be one; and
- for every maximal lattice line \(L\) in \(G_{77}\) containing at least
  three grid cells, impose
  \[
  \sum_v |L\cap O_v|\,y_v\le2,
  \]
  where \(O_v\) is the cell set represented by variable \(v\).  Cells of the
  fixed-empty anti-diagonal contribute no variable.

Expanding a satisfying assignment produces a 154-point no-three-in-line
rct4-subclass set, and every 154-point no-three-in-line rct4-subclass set
produces exactly one satisfying assignment.  This is the complete claim in
[`claims.json`](claims.json).

The claim makes no assertion about the number or digest of constraints
produced by any implementation, whether a satisfying assignment exists,
solver behavior, general half-turn configurations, reflection-symmetric or
asymmetric configurations, classification of rotations, or the value of
\(D(77)\).

## Proof

### The cells form the required variable partition

The center \((38,38)\) lies on the fixed-empty anti-diagonal.  The other 76
main-diagonal cells form the 38 disjoint antipodal pairs

\[
D_i=\{(i,i),(76-i,76-i)\},\qquad 0\le i<38.
\]

Every cell off both diagonals has a four-element orbit under \(\rho\).  Such
an orbit cannot meet either diagonal: applying \(\rho\) sends the main
diagonal to the anti-diagonal and conversely, so an orbit meeting a diagonal
would not be an off-diagonal orbit.  Distinct group-action orbits are
disjoint.  Thus the four-element off-diagonal orbits and the 38 pairs
\(D_i\) partition \(G_{77}\setminus A\) into exactly the variable cell sets
used in the encoding.

It follows directly from the definition of the subclass that each rct4 set
has a unique Boolean assignment: a variable is one precisely when its entire
cell set is occupied.  Conversely every Boolean assignment expands uniquely
to an rct4-subclass set.

Selecting 38 off-diagonal variables and one diagonal-pair variable gives

\[
38\cdot4+1\cdot2=154
\]

distinct occupied cells.  Hence the two cardinality equations are equivalent
to the required size inside this subclass.

### The line inequalities are exactly no-three-in-line

For a fixed assignment, the number of expanded occupied cells on a maximal
lattice line \(L\) is exactly

\[
|S\cap L|=\sum_v |L\cap O_v|\,y_v.
\]

This equality is literal counting: the variable cell sets are disjoint and
the only omitted cells belong to the anti-diagonal, which is fixed empty.
Therefore the inequality attached to \(L\) holds if and only if \(L\)
contains at most two selected cells.

If an expanded set contains three collinear points, their common Euclidean
line intersects \(G_{77}\) in a unique maximal lattice line containing at
least those three grid cells, so the corresponding inequality is violated.
Conversely, a violated inequality exhibits at least three selected cells on
one line and hence a collinear triple.  Thus all line inequalities hold if
and only if the expanded set is no-three-in-line.

Combining this equivalence with the unique variable partition and cardinality
calculation proves both directions of the claim.

## Relationship to earlier work

Transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce` introduced the rct4
model but coupled the restricted encoding with an incorrect assertion that it
was the unique viable rotational route.  Transaction
`046e8f269922a6d2ce37ce17d4878ccdb0aa7721` removed that scope error and
supplied a deterministic implementation, but its compound claim also made an
exact generated constraint count and serialization digest material.  Its
validity-v2 report affirmatively verified the subclass partition, cardinality
encoding, maximal-line argument, and soundness and completeness proved above,
while withholding validity only for those generated statistics.

This contribution isolates the already checkable mathematical encoding
theorem.  Neither earlier transaction is a logical premise: the definitions
and proof needed for this claim are complete here.  They are cited only for
provenance and attribution, and no invalid or indeterminate submission is
declared as a dependency.

## Limitations

The rct4 subclass is strictly smaller than the class of centered-half-turn
configurations.  A general half-turn-invariant set may choose arbitrary
antipodal pairs without selecting complete quarter-turn orbits, and it need
not have the diagonal restrictions imposed above.  Even an infeasibility
proof for this Boolean system would therefore exclude only this subclass and
would not improve the global upper bound on \(D(77)\).

## Authorship

The rct4 definition and encoding construction are attributed to the earlier
transactions above and their cited mathematical sources.  This atomic
separation and proof were prepared by an OpenAI Codex solver agent at Robert
Raynor's request in response to the hardened validity-v2 assessment.
