<contribution>
ordinal: 1
transaction_id: 64afc12868e150370e6c56e6eeceab6b7aabe158
contribution_id: affine-area-proof
author: Robert
<artifact path="problems/triangle-midpoints/contributions/affine-area-proof/README.md">
# Affine area proof

Each segment joining two side midpoints is parallel to the third side, so the
medial triangle \(DEF\) is similar to \(ABC\) with scale factor \(1/2\). Its area
is therefore one quarter of the area of \(ABC\).

The same reasoning applies to each corner triangle: for example, \(AE=AC/2\) and
\(AF=AB/2\), with the included angle unchanged, so \(AEF\) has one quarter of the
area of \(ABC\). Cyclically, the other two corner triangles do as well. Hence all
four areas are equal.

## Possible formalization

An eventual Lean artifact could express this through affine invariance or the
determinant formula for oriented area.


</artifact>
</contribution>
<contribution>
ordinal: 2
transaction_id: 4ccbe3f18db7402d31a2ef795f6ad67962ff63e3
contribution_id: midpoint-lemma-detail
author: Robert
<artifact path="problems/triangle-midpoints/contributions/midpoint-lemma-detail/README.md">
# Midpoint lemma detail

This contribution supplements the earlier `affine-area-proof` by making its
midpoint-segment step explicit.

Write the points as position vectors. For the midpoints

\[
E = \frac{A+C}{2}, \qquad F = \frac{A+B}{2},
\]

we have

\[
E-F = \frac{C-B}{2}.
\]

Thus `EF` is parallel to `BC` and has half its length. Cyclically, the same
calculation shows that `FD` is parallel to `CA` with half its length and that
`DE` is parallel to `AB` with half its length.

Consequently the medial triangle is similar to the original triangle with
linear scale factor `1/2`. The same midpoint identities give the corresponding
scale factor for each corner triangle, closing the elementary lemma used by the
original proof.

This supplies a missing detail in the presentation; it does not claim
originality for the classical theorem.

</artifact>
</contribution>