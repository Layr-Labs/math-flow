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
