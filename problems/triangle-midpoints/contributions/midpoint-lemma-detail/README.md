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
