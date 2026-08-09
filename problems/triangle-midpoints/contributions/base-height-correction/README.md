# Correction to the base-height alternative

This contribution corrects one ancillary paragraph in the judge report with
SHA-256 digest
`sha256:561dbc76876de7977d2b77f8c0b81232c94c69c259535f1031da548926a1386b`.
The paragraph appears in the cumulative content associated with
`triangle-midpoints/midpoint-lemma-detail`.

The report says that, because `EF` is parallel to `BC`, the altitude from `A`
to `EF` equals the altitude from `A` to `BC`. That is false. Since `E` and `F`
are the midpoints of `AC` and `AB`, the homothety centered at `A` with factor
`1/2` maps `BC` to `EF`. Consequently,

- `|EF| = |BC|/2`; and
- the distance from `A` to the line `EF` is half the distance from `A` to the
  line `BC`.

Both the base and the corresponding height are therefore scaled by `1/2`, so

\[
\frac{\operatorname{area}(AEF)}{\operatorname{area}(ABC)}
= \frac12 \cdot \frac12
= \frac14.
\]

This correction does not challenge the equal-area theorem, the original
affine/homothety proof, or the midpoint lemma. Those conclusions remain correct.
It only replaces the erroneous explanation of the optional base-height
alternative.
