<contribution>
ordinal: 4
transaction_id: 29ccbd396781fd36d436ed2e6d0952a4730361b9
contribution_id: finite-rotation-classification-proof
author: Robert Raynor
<artifact path="problems/no-three-in-line-77/contributions/finite-rotation-classification-proof/README.md">
# Arbitrary-center rotational symmetry at cardinalities 153 and 154

## Result

This contribution closes the specific arbitrary-center gap recorded in
`d77/rotational-classification-scope`.

**Finite-rotation lemma.** Let \(S\subset\mathbb Z^2\) be finite and
noncollinear. If a nonidentity Euclidean rotation \(T\) satisfies \(T(S)=S\),
then \(T\) is a half-turn or a quarter-turn (in either orientation). This
allows an arbitrary center; no assumption is made that the rotation preserves
the whole ambient square or the whole integer lattice.

Consequently, for a no-three-in-line set \(S\subset G_{77}\):

1. if \(|S|=153\), then \(S\) has no nontrivial rotational symmetry;
2. if \(|S|=154\) and \(S\) has nontrivial rotational symmetry, it is invariant
   under the half-turn about \((38,38)\), and \((38,38)\notin S\).

This classifies rotations only. It says nothing about reflection symmetry and
does not identify the strict rct4 subclass with the full centered half-turn
class. In particular, it does **not** improve the certified interval

\[
152\le D(77)\le154.
\]

## Proof of the finite-rotation lemma

Write the rotation as

\[
T(x)=z+Q(x-z),\qquad
Q=\begin{pmatrix}c&-s\\s&c\end{pmatrix},
\qquad c^2+s^2=1.
\]

Here \(z\in\mathbb R^2\) is arbitrary. We prove first that both \(c\) and
\(s\) are rational.

Choose noncollinear \(p_0,p_1,p_2\in S\), and form the matrices whose columns
are two differences and their rotated images:

\[
B=\begin{pmatrix}|&|\\p_1-p_0&p_2-p_0\\|&|\end{pmatrix},
\qquad
C=\begin{pmatrix}|&|\\T(p_1)-T(p_0)&T(p_2)-T(p_0)\\|&|\end{pmatrix}.
\]

The columns of \(B\) and \(C\) are integer vectors because all six relevant
points lie in \(S\subset\mathbb Z^2\). Noncollinearity gives
\(\det(B)\ne0\). The translational part of \(T\) cancels in differences, so

\[
C=QB,
\qquad Q=CB^{-1}.
\]

The inverse of the nonsingular integer matrix \(B\) has rational entries.
Thus \(Q\) has rational entries, and in particular \(c,s\in\mathbb Q\).
This step does not require the center \(z\) to be a lattice point.

Next, \(T\) acts as a permutation of the finite set \(S\). Some positive
power of that permutation is the identity, so for some \(m\ge1\), \(T^m\)
fixes every point of \(S\). Since \(S\) contains three noncollinear points,
the Euclidean isometry \(T^m\) is the identity. Hence \(Q\) has finite order.

Let \(\lambda,\lambda^{-1}\) be the complex eigenvalues of \(Q\). They are
roots of unity, so

\[
t=\operatorname{tr}(Q)=\lambda+\lambda^{-1}=2c
\]

is an algebraic integer. But \(Q\) is rational, hence \(t\in\mathbb Q\); a
rational algebraic integer is an integer. Since \(|t|\le2\),

\[
t\in\{-2,-1,0,1,2\}.
\]

The cases \(t=\pm1\) would give \(c=\pm\tfrac12\), and then
\(s^2=1-c^2=\tfrac34\). This is impossible because \(s\) was proved rational
whereas \(\sqrt3/2\) is irrational. The case \(t=2\) is the identity rotation,
which was excluded. If \(t=-2\), then \((c,s)=(-1,0)\), a half-turn. If
\(t=0\), then \((c,s)=(0,\pm1)\), a quarter-turn. These are all cases, proving
the lemma.

## Application to \(G_{77}\)

A 153- or 154-point no-three-in-line set is noncollinear, so the lemma applies.
It remains only to combine it with the orbit arguments already represented in
`rotational-symmetry/cardinality-obstructions`; they are repeated here to make
the corollary self-contained.

Under a half-turn, noncentral points occur in opposite pairs. If an invariant
set has odd size, it contains the center. Any other opposite pair together with
that center would be three collinear points. Therefore a half-turn-invariant
no-three-in-line set of odd size has at most one point, excluding size 153.

Under a quarter-turn, every noncentral orbit has size four. If the center is
selected, the same half-turn argument excludes every other orbit; otherwise the
cardinality is divisible by four. Thus neither 153 nor 154 is compatible with
a quarter-turn.

The only remaining nontrivial rotation at size 154 is a half-turn. A
154-point no-three-in-line subset of \(G_{77}\) has exactly two selected points
in every row and, independently, exactly two in every column: each of the 77
rows or columns contains at most two points, and equality holds in the total
bound \(154=2\cdot77\). Its coordinatewise bounding box is therefore all of
\([0,76]^2\). A half-turn maps the bounding box of an invariant set to itself,
so its center is the center of that box, \((38,38)\). The rotation has no
selected fixed point: otherwise every opposite pair and the center would be a
collinear triple (and, equivalently here, 154 is even while all noncentral
orbits have size two). Hence \((38,38)\notin S\).

This proves both stated consequences.

## Provenance and relationship to prior work

- Research-direction registration:
  `a9552d14dcd11d394a0ae9672b6d81dae033f127`.
- The qualified knowledge node addressed is
  `d77/rotational-classification-scope`, revision
  `sha256:49933934edbd64cdd3484e6a987ffcb1a4bde2c1beb63aaddad89d78736e22db`.
- The accepted half-turn and quarter-turn orbit facts are represented by
  `rotational-symmetry/cardinality-obstructions`, revision
  `sha256:586ea4ca1f07e8217cbd39b0496d0330f895b088623f0429c214c93a88b1aa83`.
- Both nodes arose from transaction
  `c98dd877ad81611a9a469b1bd790cd909b56b1ce` and its primary judgment
  `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`.
  That judgment explicitly identified the finite-order classification step as
  plausible but omitted. This contribution supplies that step and reuses the
  already established orbit and occupancy arguments; it claims no priority for
  those prior results or for the rct4 model.

No external mathematical source or computational result is used.

## Verification and limitations

The evidence is the exact proof above, not a bounded computation. Repository
validation can be reproduced from the repository root with:

```bash
python3 -m math_flow validate-tree
python3 -m unittest discover -s tests -v
git diff --check
```

Known limitations are deliberate:

- the theorem classifies Euclidean rotations preserving a finite noncollinear
  lattice set, not reflections, general affine maps, or approximate symmetry;
- the 154-point conclusion is conditional and constructs no configuration;
- no 153- or 154-point existence or global nonexistence result is obtained;
- the rct4 model remains a strict subclass of centered half-turn symmetry; and
- the certified bounds remain unchanged.

## Authorship

Proof and exposition by an OpenAI Codex research agent working through the
Math Flow solver protocol at Robert Raynor's request. Prior results and their
immutable provenance are credited above.

</artifact>
</contribution>
<contribution>
ordinal: 5
transaction_id: 0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0
contribution_id: record-152-objective-verification
author: Robert Raynor
<artifact path="problems/no-three-in-line-77/contributions/record-152-objective-verification/README.md">
# Replayable objective verification of the 152-point record

This contribution republishes the exact `record-152-certificate` checker and
certificate bytes with a canonical `verification.json` request. Its purpose is
to produce a durable, independently replayable objective attestation through
Math Flow's trusted hosted verifier path.

## Scope

The encoded configuration is byte-for-byte identical, and the checker logic is
identical, to the artifacts in the earlier canonical contribution
`record-152-certificate` (transaction
`dfc0cc40d1193b8d5ca25e7f177fa48ff9a1b38d`). The checker establishes that the
payload decodes to 152 distinct points in the `76 x 76` grid and that every
triple has nonzero integer determinant. Since that grid embeds into the
`77 x 77` grid, this re-verifies the existing lower bound

\[
D(77) \ge 152.
\]

This is independent verification infrastructure, not a new bound and not a
claim about optimality. A successful attestation proves only that the pinned
checker accepted these pinned bytes in the governed environment; judgment of
whether the encoding captures the stated mathematics remains separate.

## Reproduction

Run locally with Python 3 and the standard library:

```bash
python3 -I -B verify.py configuration.txt
```

The expected output is:

```text
verified 152 points on a 76 x 76 grid; no collinear triple
```

After canonical merge, `verification.json` requests the repository-approved
`python-stdlib-3-13-v1` verifier. The trusted workflow should execute it in the
digest-pinned, networkless, read-only OCI environment and publish the resulting
content-addressed attestation separately on the `projections` branch.

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-objective-verification/configuration.txt">
obgOoUWblJogsLxKkpzMZKjqzIVxy8BDk6DMeh$Q[&!5(w@BV8>14muQd3a7FA<q$I<05YfH@Rl]{03Sm9wYf){2vCN2&y!d]anJR[>1?i%9H6)7A4nCWZr#(T#%?FGivENUterEOTtGsLXPuSchjPpXc

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-objective-verification/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify.py",
  "arguments": ["configuration.txt"]
}

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-objective-verification/verify.py">
from __future__ import annotations

import argparse
import itertools
from pathlib import Path


ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "#$%&@?!()[]<>{}=*+|-/~^_:;,."
)


def decode(value: str) -> tuple[int, list[tuple[int, int]]]:
    encoded = value.strip()
    if not encoded:
        raise ValueError("configuration is empty")
    if encoded[0] not in ".:/-ocx+*":
        raise ValueError("configuration has no recognized symmetry marker")
    payload = encoded[1:]
    if not payload or len(payload) % 2:
        raise ValueError("configuration payload must contain two columns per row")
    size = len(payload) // 2
    try:
        points = [
            (ALPHABET.index(payload[2 * row + offset]), row)
            for row in range(size)
            for offset in range(2)
        ]
    except ValueError as exc:
        raise ValueError("configuration contains a character outside the alphabet") from exc
    return size, points


def determinant(
    first: tuple[int, int],
    second: tuple[int, int],
    third: tuple[int, int],
) -> int:
    return (second[0] - first[0]) * (third[1] - first[1]) - (
        third[0] - first[0]
    ) * (second[1] - first[1])


def verify(path: Path) -> tuple[int, int]:
    size, points = decode(path.read_text(encoding="utf-8"))
    if len(set(points)) != len(points):
        raise ValueError("configuration contains a duplicate point")
    if any(not (0 <= x < size and 0 <= y < size) for x, y in points):
        raise ValueError("configuration contains a point outside its grid")
    for triple in itertools.combinations(points, 3):
        if determinant(*triple) == 0:
            raise ValueError(f"collinear triple: {triple}")
    return size, len(points)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("configuration", type=Path)
    args = parser.parse_args()
    size, count = verify(args.configuration)
    print(f"verified {count} points on a {size} x {size} grid; no collinear triple")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

</artifact>
</contribution>
<contribution>
ordinal: 9
transaction_id: 87f78eb20d47a1db7d4ef35702bf00b4af94ad8d
contribution_id: rct4-154-subclass-encoding-theorem
author: Robert Raynor
<artifact path="problems/no-three-in-line-77/contributions/rct4-154-subclass-encoding-theorem/README.md">
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

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/rct4-154-subclass-encoding-theorem/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "no-three-in-line-77/rct4-154-subclass-encoding-theorem",
      "statement": "Let rho(x,y)=(y,76-x), and define the rct4 subclass of G_77 to consist exactly of sets with empty anti-diagonal, occupied off-diagonal cells equal to unions of complete four-cell rho-orbits, and main-diagonal intersection equal to exactly one antipodal pair. Give each such four-cell orbit and diagonal pair a Boolean variable, require exactly 38 four-orbit variables and one diagonal-pair variable, and for every maximal lattice line L with at least three grid cells require the weighted inequality sum_v |L intersect O_v| y_v at most 2. Expanding a satisfying assignment gives a 154-point no-three-in-line member of the rct4 subclass, and every 154-point no-three-in-line member of that subclass gives exactly one satisfying assignment. This claim makes no assertion about an implementation-specific constraint count or digest, satisfiability or infeasibility, any larger symmetry class, classification of rotations, or the value of D(77).",
      "dependencyTransactionIds": []
    }
  ]
}

</artifact>
</contribution>
<contribution>
ordinal: 10
transaction_id: 17928a941d7503ff0dc32740b707f475728300a3
contribution_id: record-152-eight-embedding-rigidity-attested
author: Robert Raynor
<artifact path="problems/no-three-in-line-77/contributions/record-152-eight-embedding-rigidity-attested/README.md">
# Governed eight-embedding local rigidity certificate

## One claim and its exact scope

This contribution makes the single claim declared in
[`claims.json`](claims.json). The included
[`configuration.txt`](configuration.txt) decodes to a 152-point
no-three-in-line subset \(C\) of
\(G_{76}=\{0,\ldots,75\}^2\). Exact exhaustive computation establishes
that \(C\) is invariant under a quarter turn, has two distinct dihedral
images, and therefore has exactly eight distinct embeddings in \(G_{77}\):
the two images translated by the four vectors in \(\{0,1\}^2\).

For each of those eight embeddings \(E\), the included
[`rigidity.py`](rigidity.py) establishes all of the following:

1. every cell outside \(E\) is blocked by at least two distinct unordered
   pairs of points of \(E\);
2. deleting any one point of \(E\) frees no originally outside cell;
3. deleting any unordered pair of points of \(E\) frees at most one
   originally outside cell; and
4. exactly 16 unordered deletion pairs per embedding free one cell.

Consequently, if a no-three-in-line set \(S\subseteq G_{77}\) satisfies
\(|E\setminus S|\leq2\), then \(|S\setminus E|\leq1\) and
\(|S|\leq152\). Thus any such \(S\) with at least 153 points has
\(|E\setminus S|\geq3\), \(|S\setminus E|\geq4\), and symmetric
difference at least seven from every one of the eight embeddings.

This is a local statement about these eight embeddings only. It does not
classify arbitrary 152-point configurations, exclude other construction
families, prove an upper bound for \(D(77)\), or claim global optimality.

## Self-contained evidence

The three normative evidence files are local to this contribution:

```text
configuration.txt  a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4
rigidity.py         f38a91c67f0cc9a3505c49e21b06515d7b470286af6041cc23127fb0cb6da4d8
results.json        3d33115ac06da925edcfe6be64dd292124d1de525c8341ab23ccbc0c155737a5
```

The checker reads the included configuration directly. It first checks all
\(\binom{152}{3}=573800\) triples of the base configuration with exact
integer determinants. It then reconstructs every dihedral image and
translation, verifies that there are exactly eight distinct embeddings,
performs a complete per-cell line census, and independently reconstructs the
same blocking-pair table by walking every lattice line through every pair.
Every reported freeing is finally checked by direct determinant simulation.
The recomputed, fully enumerated census must be byte-for-byte equal to
[`results.json`](results.json).

Run from this directory using only the Python standard library:

```bash
python3 -I -B rigidity.py
```

The run is deterministic, uses exact integer arithmetic, has no network
access or external package dependency, and writes no file in verification
mode. Use `--write` only to regenerate the committed results during an
independent audit.

## Governed verification

[`verification.json`](verification.json) requests the approved
`python-stdlib-3-13-v1` verifier at canonical spec digest

```text
sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884
```

to execute `rigidity.py` in the pinned, networkless, read-only environment.
The request does not assert a hosted result. After merge, the terminal
attestation is published separately on the projections branch and binds the
exit status and output digests to the exact committed input manifest.

## Dependency and provenance

Canonical transaction
`bf1301b6b472841276f79852c2e7fe0499309684` is the sole declared reference.
It contains the same configuration bytes and has a VALID validity-v3
assessment backed by a successful governed replay. Declaring it preserves
the certificate's provenance and makes that bounded, valid evidence
available to the judge.

The mathematical local-rigidity assertion does not require an opaque earlier
certificate transaction: this contribution includes the exact configuration,
checks its no-three-in-line property again, and performs the entire local
census itself. In particular,
`dfc0cc40d41105292a119840dcdbe6f22860cf43` is historical provenance
reachable through the valid governed replay, not a declared premise here.
Transactions `c5e8096d942d57228bb4fed00f7617fb6b43af9f` and
`3baf1c8586af31bbd6509d0fd3e552658c03673b` are superseded attempts at this
local result, and `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0` is not used.
None of those historical transactions is a dependency of the claim.

This repair was prepared and exhaustively replayed by an OpenAI Codex solver
agent at Robert Raynor's request. The underlying record configuration retains
its prior mathematical provenance.

## Limits of the certificate

- The hosted attestation checks the pinned program and files; it is not an
  algorithmically independent proof.
- The exhaustive conclusion is only the stated depth-two neighborhood of the
  eight embeddings.
- No conclusion about the exact value of \(D(77)\) follows.

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-eight-embedding-rigidity-attested/claims.json">
{
  "schemaVersion": 1,
  "claims": [
    {
      "claimKey": "no-three-in-line-77/record-152-eight-embedding-rigidity-attested",
      "statement": "The included configuration.txt has SHA-256 digest a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4 and decodes to a 152-point no-three-in-line subset C of G_76. It is invariant under a quarter turn, its dihedral orbit has exactly two distinct images, and translating those images by the four vectors in {0,1}^2 gives exactly eight distinct embeddings E in G_77. For each of those eight E, every cell of G_77 minus E is blocked by at least two distinct unordered pairs of E; deleting any one point of E frees no originally outside cell; deleting any unordered pair frees at most one originally outside cell; and exactly 16 deletion pairs per E free one cell. Consequently, every no-three-in-line S in G_77 with |E minus S| at most 2 has |S minus E| at most 1 and |S| at most 152; hence |S| at least 153 implies |E minus S| at least 3, |S minus E| at least 4, and symmetric difference at least 7. This claim concerns only those eight embeddings, not arbitrary record configurations or the global value of D(77).",
      "dependencyTransactionIds": [
        "bf1301b6b472841276f79852c2e7fe0499309684"
      ]
    }
  ]
}

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-eight-embedding-rigidity-attested/configuration.txt">
obgOoUWblJogsLxKkpzMZKjqzIVxy8BDk6DMeh$Q[&!5(w@BV8>14muQd3a7FA<q$I<05YfH@Rl]{03Sm9wYf){2vCN2&y!d]anJR[>1?i%9H6)7A4nCWZr#(T#%?FGivENUterEOTtGsLXPuSchjPpXc

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-eight-embedding-rigidity-attested/results.json">
{
  "baseConfiguration": {
    "distinctDihedralImages": 2,
    "fileSha256": "sha256:a23f1f55d9a914cff49fb6ba369b9f392f7af4c5ce08085267b3af1e7d7742c4",
    "grid": 76,
    "points": 152,
    "pointsDigest": "sha256:68fcc40abed16756b2ffdc3a996f3bf1b679cfa2742583a8c9421aa69a817289",
    "quarterTurnSymmetric": true,
    "source": "configuration.txt"
  },
  "conclusions": {
    "everyEmbeddingIsMaximalInG77": true,
    "maxCellsFreedByRemovals": {
      "0": 0,
      "1": 0,
      "2": 1
    },
    "statement": "For each of the 8 embeddings E of the certified 152-point record into G_77 and every no-three-in-line set S in G_77 with |E \\ S| <= 2, it holds that |S \\ E| <= 1 and hence |S| <= 152. Any no-three-in-line set of 153 or more points therefore omits at least 3 points of every embedding, contains at least 4 points outside it, and has symmetric difference at least 7 with every embedding."
  },
  "embeddings": [
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "anti-transpose",
        "flip-x",
        "flip-y",
        "transpose"
      ],
      "index": 0,
      "minBlockingPairsPerCell": 2,
      "offset": [
        0,
        0
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            10,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              20
            ],
            [
              14,
              11
            ]
          ]
        },
        {
          "freedCell": [
            10,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              20
            ],
            [
              23,
              11
            ]
          ]
        },
        {
          "freedCell": [
            10,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              45
            ],
            [
              14,
              11
            ]
          ]
        },
        {
          "freedCell": [
            10,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              45
            ],
            [
              23,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              52
            ],
            [
              20,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              52
            ],
            [
              45,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              61
            ],
            [
              20,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              61
            ],
            [
              45,
              65
            ]
          ]
        },
        {
          "freedCell": [
            64,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              10
            ],
            [
              64,
              14
            ]
          ]
        },
        {
          "freedCell": [
            64,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              10
            ],
            [
              64,
              23
            ]
          ]
        },
        {
          "freedCell": [
            65,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              64
            ],
            [
              65,
              30
            ]
          ]
        },
        {
          "freedCell": [
            65,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              64
            ],
            [
              65,
              55
            ]
          ]
        },
        {
          "freedCell": [
            64,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              10
            ],
            [
              64,
              14
            ]
          ]
        },
        {
          "freedCell": [
            64,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              10
            ],
            [
              64,
              23
            ]
          ]
        },
        {
          "freedCell": [
            65,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              64
            ],
            [
              65,
              30
            ]
          ]
        },
        {
          "freedCell": [
            65,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              64
            ],
            [
              65,
              55
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:14ba631834b13d4224c8e88db8afa56840b3b87004aaffb6acb4ea5c81f4f86a",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "anti-transpose",
        "flip-x",
        "flip-y",
        "transpose"
      ],
      "index": 1,
      "minBlockingPairsPerCell": 2,
      "offset": [
        0,
        1
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            10,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              21
            ],
            [
              14,
              12
            ]
          ]
        },
        {
          "freedCell": [
            10,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              21
            ],
            [
              23,
              12
            ]
          ]
        },
        {
          "freedCell": [
            10,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              46
            ],
            [
              14,
              12
            ]
          ]
        },
        {
          "freedCell": [
            10,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              46
            ],
            [
              23,
              12
            ]
          ]
        },
        {
          "freedCell": [
            11,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              53
            ],
            [
              20,
              66
            ]
          ]
        },
        {
          "freedCell": [
            11,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              53
            ],
            [
              45,
              66
            ]
          ]
        },
        {
          "freedCell": [
            11,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              62
            ],
            [
              20,
              66
            ]
          ]
        },
        {
          "freedCell": [
            11,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              62
            ],
            [
              45,
              66
            ]
          ]
        },
        {
          "freedCell": [
            64,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              11
            ],
            [
              64,
              15
            ]
          ]
        },
        {
          "freedCell": [
            64,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              11
            ],
            [
              64,
              24
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              65
            ],
            [
              65,
              31
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              65
            ],
            [
              65,
              56
            ]
          ]
        },
        {
          "freedCell": [
            64,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              11
            ],
            [
              64,
              15
            ]
          ]
        },
        {
          "freedCell": [
            64,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              11
            ],
            [
              64,
              24
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              65
            ],
            [
              65,
              31
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              65
            ],
            [
              65,
              56
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:7bebe4f189f91ec8d2bb4e0e2789115e513f5f5546a55523796d7ae505d96321",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "anti-transpose",
        "flip-x",
        "flip-y",
        "transpose"
      ],
      "index": 2,
      "minBlockingPairsPerCell": 2,
      "offset": [
        1,
        0
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              20
            ],
            [
              15,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              20
            ],
            [
              24,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              45
            ],
            [
              15,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              45
            ],
            [
              24,
              11
            ]
          ]
        },
        {
          "freedCell": [
            12,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              52
            ],
            [
              21,
              65
            ]
          ]
        },
        {
          "freedCell": [
            12,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              52
            ],
            [
              46,
              65
            ]
          ]
        },
        {
          "freedCell": [
            12,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              61
            ],
            [
              21,
              65
            ]
          ]
        },
        {
          "freedCell": [
            12,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              61
            ],
            [
              46,
              65
            ]
          ]
        },
        {
          "freedCell": [
            65,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              10
            ],
            [
              65,
              14
            ]
          ]
        },
        {
          "freedCell": [
            65,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              10
            ],
            [
              65,
              23
            ]
          ]
        },
        {
          "freedCell": [
            66,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              64
            ],
            [
              66,
              30
            ]
          ]
        },
        {
          "freedCell": [
            66,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              64
            ],
            [
              66,
              55
            ]
          ]
        },
        {
          "freedCell": [
            65,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              10
            ],
            [
              65,
              14
            ]
          ]
        },
        {
          "freedCell": [
            65,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              10
            ],
            [
              65,
              23
            ]
          ]
        },
        {
          "freedCell": [
            66,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              64
            ],
            [
              66,
              30
            ]
          ]
        },
        {
          "freedCell": [
            66,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              64
            ],
            [
              66,
              55
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:946707adcb4a66c1aed85222908e31b393541d3713683776f043cc41f7b8e346",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "anti-transpose",
        "flip-x",
        "flip-y",
        "transpose"
      ],
      "index": 3,
      "minBlockingPairsPerCell": 2,
      "offset": [
        1,
        1
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            11,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              21
            ],
            [
              15,
              12
            ]
          ]
        },
        {
          "freedCell": [
            11,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              21
            ],
            [
              24,
              12
            ]
          ]
        },
        {
          "freedCell": [
            11,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              46
            ],
            [
              15,
              12
            ]
          ]
        },
        {
          "freedCell": [
            11,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              46
            ],
            [
              24,
              12
            ]
          ]
        },
        {
          "freedCell": [
            12,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              53
            ],
            [
              21,
              66
            ]
          ]
        },
        {
          "freedCell": [
            12,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              53
            ],
            [
              46,
              66
            ]
          ]
        },
        {
          "freedCell": [
            12,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              62
            ],
            [
              21,
              66
            ]
          ]
        },
        {
          "freedCell": [
            12,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              62
            ],
            [
              46,
              66
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              11
            ],
            [
              65,
              15
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              11
            ],
            [
              65,
              24
            ]
          ]
        },
        {
          "freedCell": [
            66,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              65
            ],
            [
              66,
              31
            ]
          ]
        },
        {
          "freedCell": [
            66,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              65
            ],
            [
              66,
              56
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              11
            ],
            [
              65,
              15
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              11
            ],
            [
              65,
              24
            ]
          ]
        },
        {
          "freedCell": [
            66,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              65
            ],
            [
              66,
              31
            ]
          ]
        },
        {
          "freedCell": [
            66,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              65
            ],
            [
              66,
              56
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:a5957de9bdb6125b15a8bc758a147a174ba9d1de0e5558bd0098b1e45ed3813d",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "identity",
        "rot180",
        "rot270",
        "rot90"
      ],
      "index": 4,
      "minBlockingPairsPerCell": 2,
      "offset": [
        0,
        0
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            10,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              30
            ],
            [
              14,
              64
            ]
          ]
        },
        {
          "freedCell": [
            10,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              30
            ],
            [
              23,
              64
            ]
          ]
        },
        {
          "freedCell": [
            10,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              55
            ],
            [
              14,
              64
            ]
          ]
        },
        {
          "freedCell": [
            10,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              55
            ],
            [
              23,
              64
            ]
          ]
        },
        {
          "freedCell": [
            11,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              14
            ],
            [
              20,
              10
            ]
          ]
        },
        {
          "freedCell": [
            11,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              14
            ],
            [
              45,
              10
            ]
          ]
        },
        {
          "freedCell": [
            11,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              23
            ],
            [
              20,
              10
            ]
          ]
        },
        {
          "freedCell": [
            11,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              23
            ],
            [
              45,
              10
            ]
          ]
        },
        {
          "freedCell": [
            64,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              65
            ],
            [
              64,
              52
            ]
          ]
        },
        {
          "freedCell": [
            64,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              65
            ],
            [
              64,
              61
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              11
            ],
            [
              65,
              20
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              11
            ],
            [
              65,
              45
            ]
          ]
        },
        {
          "freedCell": [
            64,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              65
            ],
            [
              64,
              52
            ]
          ]
        },
        {
          "freedCell": [
            64,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              65
            ],
            [
              64,
              61
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              11
            ],
            [
              65,
              20
            ]
          ]
        },
        {
          "freedCell": [
            65,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              11
            ],
            [
              65,
              45
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:68fcc40abed16756b2ffdc3a996f3bf1b679cfa2742583a8c9421aa69a817289",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "identity",
        "rot180",
        "rot270",
        "rot90"
      ],
      "index": 5,
      "minBlockingPairsPerCell": 2,
      "offset": [
        0,
        1
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            10,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              31
            ],
            [
              14,
              65
            ]
          ]
        },
        {
          "freedCell": [
            10,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              31
            ],
            [
              23,
              65
            ]
          ]
        },
        {
          "freedCell": [
            10,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              56
            ],
            [
              14,
              65
            ]
          ]
        },
        {
          "freedCell": [
            10,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              10,
              56
            ],
            [
              23,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              15
            ],
            [
              20,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              15
            ],
            [
              45,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              24
            ],
            [
              20,
              11
            ]
          ]
        },
        {
          "freedCell": [
            11,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              24
            ],
            [
              45,
              11
            ]
          ]
        },
        {
          "freedCell": [
            64,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              66
            ],
            [
              64,
              53
            ]
          ]
        },
        {
          "freedCell": [
            64,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              30,
              66
            ],
            [
              64,
              62
            ]
          ]
        },
        {
          "freedCell": [
            65,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              12
            ],
            [
              65,
              21
            ]
          ]
        },
        {
          "freedCell": [
            65,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              52,
              12
            ],
            [
              65,
              46
            ]
          ]
        },
        {
          "freedCell": [
            64,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              66
            ],
            [
              64,
              53
            ]
          ]
        },
        {
          "freedCell": [
            64,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              55,
              66
            ],
            [
              64,
              62
            ]
          ]
        },
        {
          "freedCell": [
            65,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              12
            ],
            [
              65,
              21
            ]
          ]
        },
        {
          "freedCell": [
            65,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              61,
              12
            ],
            [
              65,
              46
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:8229509e175d65e578f09b5129b5c96f91652ed1155e59b36d9128e5f5d60a54",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "identity",
        "rot180",
        "rot270",
        "rot90"
      ],
      "index": 6,
      "minBlockingPairsPerCell": 2,
      "offset": [
        1,
        0
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            11,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              30
            ],
            [
              15,
              64
            ]
          ]
        },
        {
          "freedCell": [
            11,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              30
            ],
            [
              24,
              64
            ]
          ]
        },
        {
          "freedCell": [
            11,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              55
            ],
            [
              15,
              64
            ]
          ]
        },
        {
          "freedCell": [
            11,
            64
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              55
            ],
            [
              24,
              64
            ]
          ]
        },
        {
          "freedCell": [
            12,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              14
            ],
            [
              21,
              10
            ]
          ]
        },
        {
          "freedCell": [
            12,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              14
            ],
            [
              46,
              10
            ]
          ]
        },
        {
          "freedCell": [
            12,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              23
            ],
            [
              21,
              10
            ]
          ]
        },
        {
          "freedCell": [
            12,
            10
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              23
            ],
            [
              46,
              10
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              65
            ],
            [
              65,
              52
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              65
            ],
            [
              65,
              61
            ]
          ]
        },
        {
          "freedCell": [
            66,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              11
            ],
            [
              66,
              20
            ]
          ]
        },
        {
          "freedCell": [
            66,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              11
            ],
            [
              66,
              45
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              65
            ],
            [
              65,
              52
            ]
          ]
        },
        {
          "freedCell": [
            65,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              65
            ],
            [
              65,
              61
            ]
          ]
        },
        {
          "freedCell": [
            66,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              11
            ],
            [
              66,
              20
            ]
          ]
        },
        {
          "freedCell": [
            66,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              11
            ],
            [
              66,
              45
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:26626de9ef89b37c197e1df635db1ba3b1ad1016c08024f11e7a642f40f67390",
      "singleRemovalFreedCells": 0
    },
    {
      "blockingIncidenceTotal": 51449,
      "imageTransforms": [
        "identity",
        "rot180",
        "rot270",
        "rot90"
      ],
      "index": 7,
      "minBlockingPairsPerCell": 2,
      "offset": [
        1,
        1
      ],
      "outsideCells": 5777,
      "pairRemovalFreeings": [
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              31
            ],
            [
              15,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              31
            ],
            [
              24,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              56
            ],
            [
              15,
              65
            ]
          ]
        },
        {
          "freedCell": [
            11,
            65
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              11,
              56
            ],
            [
              24,
              65
            ]
          ]
        },
        {
          "freedCell": [
            12,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              15
            ],
            [
              21,
              11
            ]
          ]
        },
        {
          "freedCell": [
            12,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              15
            ],
            [
              46,
              11
            ]
          ]
        },
        {
          "freedCell": [
            12,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              24
            ],
            [
              21,
              11
            ]
          ]
        },
        {
          "freedCell": [
            12,
            11
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              12,
              24
            ],
            [
              46,
              11
            ]
          ]
        },
        {
          "freedCell": [
            65,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              66
            ],
            [
              65,
              53
            ]
          ]
        },
        {
          "freedCell": [
            65,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              31,
              66
            ],
            [
              65,
              62
            ]
          ]
        },
        {
          "freedCell": [
            66,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              12
            ],
            [
              66,
              21
            ]
          ]
        },
        {
          "freedCell": [
            66,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              53,
              12
            ],
            [
              66,
              46
            ]
          ]
        },
        {
          "freedCell": [
            65,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              66
            ],
            [
              65,
              53
            ]
          ]
        },
        {
          "freedCell": [
            65,
            66
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              56,
              66
            ],
            [
              65,
              62
            ]
          ]
        },
        {
          "freedCell": [
            66,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              12
            ],
            [
              66,
              21
            ]
          ]
        },
        {
          "freedCell": [
            66,
            12
          ],
          "pattern": "two-lines-of-two",
          "remove": [
            [
              62,
              12
            ],
            [
              66,
              46
            ]
          ]
        }
      ],
      "pointsDigest": "sha256:f16b942eb3444e37b815317a1f7189bb9fb0ff7cb74e739948daa05246d8771b",
      "singleRemovalFreedCells": 0
    }
  ],
  "grid": 77,
  "problem": "no-three-in-line-77",
  "schemaVersion": 1
}

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-eight-embedding-rigidity-attested/rigidity.py">
"""Local rigidity of the certified 152-point record inside the 77 x 77 grid.

This checker establishes, by exhaustive exact-integer computation, that every
embedding of the certified 152-point no-three-in-line configuration on G_76
into G_77 is an isolated local optimum:

  1. Saturation: every cell of G_77 outside the embedded configuration is
     collinear with two configuration points, so the embedding is maximal.
  2. One-robust saturation: after removing any single configuration point,
     every outside cell is still blocked. No cell is freed.
  3. Two-removal accounting: removing any two configuration points frees at
     most one outside cell; exactly sixteen unordered removal pairs free a
     (unique) cell, and these are listed exhaustively in results.json.

Consequently, for every embedding E and every no-three-in-line set S in G_77:
if |E \\ S| <= 2 then |S \\ E| <= 1 and |S| <= 152. Hence any hypothetical
153- or 154-point configuration omits at least three points of E and contains
at least four points outside E (symmetric difference at least seven).

As a by-product the checker verifies that the decoded record configuration is
invariant under a quarter-turn rotation of G_76, so its dihedral orbit has
exactly two distinct images and the eight embeddings enumerated here (two
images times four translations) are the complete set.

Methods (both exact, no floating point, no randomness):

  * Primary "line census": for each outside cell c, group configuration
    points by the sign-normalized primitive direction of p - c. Points share
    a line through c exactly when they share a direction, so the groups of
    size >= 2 ("heavy lines") determine every blocking pair. Two distinct
    lines through c meet only at c, so a removed point lowers the census of
    at most one heavy line; freeing c with at most two removals is therefore
    possible only in the three enumerated patterns (one line of two, one line
    of three, or two lines of two).
  * Independent cross-check "line walk": for every pair of configuration
    points, walk the full lattice line through the pair in primitive steps
    and record each visited cell. Per-cell blocking-pair counts must match
    the census exactly, and freeing removal sets are re-derived from these
    explicit pair lists as minimum hitting sets and must match as well.
  * Every reported freeing is finally re-verified by direct simulation:
    remove the pair, then test the freed cell against all remaining pairs
    with the standard 2x2 determinant.

Usage (from this directory):

    python3 rigidity.py            # verify every claim against results.json
    python3 rigidity.py --write    # regenerate results.json

Exits nonzero (with a message) if any claim or the committed results fail.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from collections import defaultdict
from math import gcd
from pathlib import Path

ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "#$%&@?!()[]<>{}=*+|-/~^_:;,."
)

SMALL = 76  # grid of the certified record
BIG = 77  # target grid
POINTS = 152

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIGURATION = HERE / "configuration.txt"
DEFAULT_RESULTS = HERE / "results.json"

# The dihedral group of the 76 x 76 grid, acting on {0..75}^2 with m = 75.
DIHEDRAL = {
    "identity": lambda x, y: (x, y),
    "rot90": lambda x, y: (SMALL - 1 - y, x),
    "rot180": lambda x, y: (SMALL - 1 - x, SMALL - 1 - y),
    "rot270": lambda x, y: (y, SMALL - 1 - x),
    "flip-x": lambda x, y: (SMALL - 1 - x, y),
    "flip-y": lambda x, y: (x, SMALL - 1 - y),
    "transpose": lambda x, y: (y, x),
    "anti-transpose": lambda x, y: (SMALL - 1 - y, SMALL - 1 - x),
}

Point = tuple[int, int]


def fail(message: str) -> None:
    raise SystemExit(f"FAILED: {message}")


def decode(text: str) -> list[Point]:
    """Decode the record certificate: one marker character, then two
    alphabet-encoded x coordinates per row y = 0..75."""
    encoded = text.strip()
    payload = encoded[1:]
    if len(payload) != 2 * SMALL:
        fail(f"expected {2 * SMALL} payload characters, found {len(payload)}")
    points = []
    for row in range(SMALL):
        for offset in range(2):
            char = payload[2 * row + offset]
            if char not in ALPHABET:
                fail(f"character {char!r} outside the certificate alphabet")
            points.append((ALPHABET.index(char), row))
    return points


def det(a: Point, b: Point, c: Point) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


def assert_no_three_in_line(points: list[Point], grid: int, label: str) -> None:
    if len(points) != POINTS or len(set(points)) != POINTS:
        fail(f"{label}: expected {POINTS} distinct points")
    if any(not (0 <= x < grid and 0 <= y < grid) for x, y in points):
        fail(f"{label}: point outside the {grid} x {grid} grid")
    for triple in itertools.combinations(points, 3):
        if det(*triple) == 0:
            fail(f"{label}: collinear triple {triple}")


def primitive(dx: int, dy: int) -> Point:
    g = gcd(abs(dx), abs(dy))
    px, py = dx // g, dy // g
    if px < 0 or (px == 0 and py < 0):
        px, py = -px, -py
    return px, py


def point_set_digest(points: frozenset[Point]) -> str:
    canonical = json.dumps(sorted(points), separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("ascii")).hexdigest()


def census_heavy_lines(config: list[Point], cell: Point) -> list[list[Point]]:
    """All maximal groups of >= 2 configuration points collinear with cell."""
    groups: dict[Point, list[Point]] = defaultdict(list)
    cx, cy = cell
    for p in config:
        groups[primitive(p[0] - cx, p[1] - cy)].append(p)
    return [sorted(group) for group in groups.values() if len(group) >= 2]


def minimal_freeing_sets(heavy: list[list[Point]]) -> tuple[list[Point], list[frozenset[Point]]]:
    """Minimal removal sets of size <= 2 that unblock a cell with the given
    heavy lines. Distinct lines through the cell meet only at the cell, so a
    removal serves at most one line; each heavy line of n points needs n - 1
    removals. Only three patterns fit within two removals."""
    singletons: list[Point] = []
    pairs: list[frozenset[Point]] = []
    if len(heavy) == 1:
        line = heavy[0]
        if len(line) == 2:
            singletons.extend(line)
        elif len(line) == 3:
            pairs.extend(frozenset(pair) for pair in itertools.combinations(line, 2))
    elif len(heavy) == 2:
        first, second = heavy
        if len(first) == 2 and len(second) == 2:
            pairs.extend(frozenset((a, b)) for a in first for b in second)
    return singletons, pairs


def walk_pair_table(config: list[Point]) -> dict[Point, list[tuple[Point, Point]]]:
    """Independent construction: cell -> list of configuration pairs collinear
    with it, found by walking every pair's full lattice line inside G_77."""
    table: dict[Point, list[tuple[Point, Point]]] = defaultdict(list)
    for a, b in itertools.combinations(config, 2):
        sx, sy = primitive(b[0] - a[0], b[1] - a[1])
        for direction in (1, -1):
            k = direction
            while True:
                cell = (a[0] + k * sx, a[1] + k * sy)
                if not (0 <= cell[0] < BIG and 0 <= cell[1] < BIG):
                    break
                if cell != a and cell != b:
                    table[cell].append((a, b))
                k += direction
    return table


def hitting_sets_from_pairs(
    pairs: list[tuple[Point, Point]],
) -> tuple[list[Point], list[frozenset[Point]]]:
    """Minimal removal sets of size <= 2 covering every blocking pair,
    derived from the explicit pair list (independent of the census logic)."""
    singletons = [r for r in set(itertools.chain.from_iterable(pairs)) if all(r in p for p in pairs)]
    result: set[frozenset[Point]] = set()
    a0, b0 = pairs[0]
    for r1 in (a0, b0):
        rest = [p for p in pairs if r1 not in p]
        if not rest:
            continue  # r1 alone suffices; handled as a singleton
        candidates = set(rest[0])
        for p in rest[1:]:
            candidates &= set(p)
            if not candidates:
                break
        for r2 in candidates:
            if r2 != r1:
                result.add(frozenset((r1, r2)))
    return sorted(singletons), sorted(result, key=sorted)


def analyze_embedding(embedding: frozenset[Point]) -> dict:
    config = sorted(embedding)
    outside = [
        (x, y) for x in range(BIG) for y in range(BIG) if (x, y) not in embedding
    ]

    # Primary method: per-cell line census.
    blocking_counts: dict[Point, int] = {}
    singleton_freeings: list[tuple[Point, Point]] = []  # (removal, freed cell)
    pair_freeings: dict[frozenset[Point], list[Point]] = defaultdict(list)
    patterns: dict[Point, str] = {}
    for cell in outside:
        heavy = census_heavy_lines(config, cell)
        count = sum(len(line) * (len(line) - 1) // 2 for line in heavy)
        if count == 0:
            fail(f"saturation violated: cell {cell} is addable to an embedding")
        blocking_counts[cell] = count
        singles, pairs = minimal_freeing_sets(heavy)
        for r in singles:
            singleton_freeings.append((r, cell))
        for removal in pairs:
            pair_freeings[removal].append(cell)
        if singles or pairs:
            patterns[cell] = (
                "one-line-of-three" if len(heavy) == 1 else "two-lines-of-two"
            )

    # Independent cross-check: explicit pair lists via line walking.
    table = walk_pair_table(config)
    if set(table) != set(outside):
        fail("cross-check: walked cell set differs from the outside cells")
    for cell in outside:
        if len(table[cell]) != blocking_counts[cell]:
            fail(f"cross-check: blocking count mismatch at {cell}")
        singles, pairs = hitting_sets_from_pairs(table[cell])
        census_singles = sorted(r for r, c in singleton_freeings if c == cell)
        census_pairs = sorted(
            (rm for rm, cells in pair_freeings.items() if cell in cells), key=sorted
        )
        if singles != census_singles or pairs != census_pairs:
            fail(f"cross-check: freeing sets mismatch at {cell}")

    if singleton_freeings:
        fail(f"one-robust saturation violated: {sorted(singleton_freeings)}")

    # Direct simulation of every reported freeing.
    freeing_records = []
    for removal, cells in sorted(pair_freeings.items(), key=lambda kv: sorted(kv[0])):
        if len(cells) > 1:
            fail(f"removal pair {sorted(removal)} frees {len(cells)} cells")
        (cell,) = cells
        remaining = [p for p in config if p not in removal]
        if any(det(cell, a, b) == 0 for a, b in itertools.combinations(remaining, 2)):
            fail(f"simulation: {cell} is not actually freed by removing {sorted(removal)}")
        freeing_records.append(
            {
                "remove": sorted(removal),
                "freedCell": list(cell),
                "pattern": patterns[cell],
            }
        )

    return {
        "pointsDigest": point_set_digest(embedding),
        "outsideCells": len(outside),
        "minBlockingPairsPerCell": min(blocking_counts.values()),
        "blockingIncidenceTotal": sum(blocking_counts.values()),
        "singleRemovalFreedCells": 0,
        "pairRemovalFreeings": freeing_records,
    }


def build_results(configuration_path: Path) -> dict:
    raw = configuration_path.read_bytes()
    base = decode(raw.decode("ascii"))
    assert_no_three_in_line(base, SMALL, "base configuration")
    base_set = frozenset(base)

    rot90 = frozenset(DIHEDRAL["rot90"](x, y) for x, y in base_set)
    quarter_turn = rot90 == base_set

    images: dict[frozenset[Point], list[str]] = defaultdict(list)
    for name, transform in DIHEDRAL.items():
        images[frozenset(transform(x, y) for x, y in base_set)].append(name)

    embeddings: dict[frozenset[Point], dict] = {}
    for image, names in images.items():
        for tx, ty in ((0, 0), (0, 1), (1, 0), (1, 1)):
            embedded = frozenset((x + tx, y + ty) for x, y in image)
            if embedded not in embeddings:
                embeddings[embedded] = {
                    "imageTransforms": sorted(names),
                    "offset": [tx, ty],
                }

    embedding_reports = []
    ordered = sorted(embeddings.items(), key=lambda kv: (sorted(kv[1]["imageTransforms"]), kv[1]["offset"]))
    for index, (embedded, meta) in enumerate(ordered):
        assert_no_three_in_line(sorted(embedded), BIG, f"embedding {index}")
        started = time.time()
        report = analyze_embedding(embedded)
        report = {"index": index, **meta, **report}
        embedding_reports.append(report)
        print(
            f"embedding {index} (transforms {','.join(meta['imageTransforms'])}, "
            f"offset {tuple(meta['offset'])}): saturated, 0 single-removal freeings, "
            f"{len(report['pairRemovalFreeings'])} pair-removal freeings "
            f"[{time.time() - started:.1f}s]",
            file=sys.stderr,
        )

    return {
        "schemaVersion": 1,
        "problem": "no-three-in-line-77",
        "grid": BIG,
        "baseConfiguration": {
            "source": "configuration.txt",
            "fileSha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "points": POINTS,
            "grid": SMALL,
            "pointsDigest": point_set_digest(base_set),
            "quarterTurnSymmetric": quarter_turn,
            "distinctDihedralImages": len(images),
        },
        "embeddings": embedding_reports,
        "conclusions": {
            "everyEmbeddingIsMaximalInG77": True,
            "maxCellsFreedByRemovals": {"0": 0, "1": 0, "2": 1},
            "statement": (
                "For each of the 8 embeddings E of the certified 152-point record "
                "into G_77 and every no-three-in-line set S in G_77 with |E \\ S| <= 2, "
                "it holds that |S \\ E| <= 1 and hence |S| <= 152. Any no-three-in-line "
                "set of 153 or more points therefore omits at least 3 points of every "
                "embedding, contains at least 4 points outside it, and has symmetric "
                "difference at least 7 with every embedding."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--configuration", type=Path, default=DEFAULT_CONFIGURATION)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--write", action="store_true", help="regenerate the results file"
    )
    args = parser.parse_args()

    started = time.time()
    results = build_results(args.configuration)

    if not results["baseConfiguration"]["quarterTurnSymmetric"]:
        fail("the decoded record configuration is not quarter-turn symmetric")
    if results["baseConfiguration"]["distinctDihedralImages"] != 2:
        fail("expected exactly 2 distinct dihedral images")
    if len(results["embeddings"]) != 8:
        fail("expected exactly 8 distinct embeddings")
    for report in results["embeddings"]:
        if len(report["pairRemovalFreeings"]) != 16:
            fail(f"embedding {report['index']}: expected 16 pair-removal freeings")

    # Round-trip through JSON so tuples and lists compare canonically.
    rendered = json.dumps(
        json.loads(json.dumps(results)), indent=2, sort_keys=True
    ) + "\n"
    if args.write:
        args.results.write_text(rendered, encoding="ascii")
        print(f"wrote {args.results}", file=sys.stderr)
    elif args.results.read_text(encoding="ascii") != rendered:
        fail("computed results differ from the committed results.json")

    print(
        "verified: all 8 embeddings of the 152-point record are maximal in G_77, "
        "remain saturating after any single removal, and admit at most one freed "
        "cell after any pair removal (16 freeing pairs each; see results.json). "
        "Any 153-point or 154-point configuration, if one exists, has symmetric "
        f"difference >= 7 with every embedding. [{time.time() - started:.1f}s]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

</artifact>
<artifact path="problems/no-three-in-line-77/contributions/record-152-eight-embedding-rigidity-attested/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "rigidity.py",
  "arguments": []
}

</artifact>
</contribution>