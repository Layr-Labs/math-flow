# Finite rotational-symmetry classification

## Scope

This direction addresses the explicit proof gap recorded in knowledge node
`d77/rotational-classification-scope`. The target is the broad, arbitrary-center
meaning of rotational symmetry used by the existing contribution, rather than
only rotations in the dihedral group of the square.

The intended result is a precise lemma: every nonidentity Euclidean rotation
preserving a finite noncollinear subset of \(\mathbb Z^2\) has order two or
four. Applied to a no-three-in-line subset of \(G_{77}\) with 153 or 154
points, this reduces every possible nontrivial rotational symmetry to the
already accepted half-turn and quarter-turn cases in
`rotational-symmetry/cardinality-obstructions`.

## Method and expected evidence

Choose three noncollinear lattice points in the invariant set. Their two
independent difference vectors form a rational basis, and their rotated images
are again lattice differences, forcing the rotation's linear matrix to have
rational entries. Finiteness of the set forces the rotation to have finite
order. Its trace is then both rational and an algebraic integer, sharply
restricting the possible angles; rationality of the sine eliminates the
order-three and order-six cases.

The contribution will give this argument in full, including why invariance of
a finite noncollinear set forces finite order and why the trace restriction is
valid. It will then state exactly what follows at cardinalities 153 and 154,
without claiming any improvement to the certified interval
\(152\le D(77)\le154\).

## Relationship to existing work

Transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce` proved the half-turn,
quarter-turn, and 154-point center restrictions, but its primary judgment
`sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
explicitly found that the classification of other finite-order lattice
rotations was omitted. This direction supplies only that missing reduction. It
does not duplicate the rct4 model, identify rct4 with all centered half-turn
configurations, or attempt a new search.

## Completion criterion

The direction is complete when one atomic contribution supplies a self-contained
proof of the finite-rotation lemma and its 153/154 corollary, clearly preserves
the strict scope distinction between rct4 and general half-turn symmetry, passes
the repository validation suite, and merges as a canonical transaction.

Registration is non-exclusive and makes no claim of ownership or mathematical
correctness.
