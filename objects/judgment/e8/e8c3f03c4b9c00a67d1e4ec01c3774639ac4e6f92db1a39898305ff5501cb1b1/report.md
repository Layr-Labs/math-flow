## `no-three-in-line-77/record-152-certificate`

**Verdict: indeterminate**

### Affirmatively verified components

1. **Certificate decoding and cardinality**
   - After removing the initial marker `o`, the payload can be grouped into exactly 76 character pairs, hence the decoder constructs \(2\cdot 76=152\) points, with two points in each row \(y=0,\ldots,75\).
   - The two characters in every row-pair are different, so there are no duplicate points within a row. Points in different rows have different \(y\)-coordinates, so all 152 points are distinct.
   - Every character used has alphabet index at most \(75\). In particular, the largest-index character appearing is `{`, which has index \(75\); none of `}`, `=`, or later alphabet characters appears. Thus all points lie in \(\{0,\ldots,75\}^2\).

2. **Verifier logic**
   - `itertools.combinations(points, 3)` enumerates all
     \[
     \binom{152}{3}=573{,}800
     \]
     unordered triples of distinct listed points.
   - The determinant
     \[
     (x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1)
     \]
     vanishes exactly when the three points are collinear.
   - Python integer arithmetic is exact here, so overflow is not an issue.
   - Consequently, if the supplied program completes with the displayed success message on the supplied file, it establishes that the 152 points contain no collinear triple.

3. **Embedding implication**
   - A valid configuration in \(\{0,\ldots,75\}^2\) is unchanged when regarded as a subset of \(\{0,\ldots,76\}^2\). Therefore verified noncollinearity of this certificate would imply \(D(77)\ge 152\).

4. **Upper bound**
   - Each of the 77 horizontal rows can contain at most two selected points, since any three distinct points in one row are collinear.
   - Summing over the rows gives \(D(77)\le 2\cdot77=154\).
   - The ancillary assertion that a 154-point configuration must have exactly two points in every row and every column also follows by applying the same argument to both horizontal and vertical lines.

### Material unresolved obligation

The supplied packet contains **no terminal objective attestation**, determinant table, or other independently checkable execution trace establishing that the verifier actually completed successfully on the supplied bytes. The README’s statement that the program reports success is part of the untrusted claim being audited, not independent evidence.

Static inspection shows that the verifier would correctly reject any collinear triple, but it does not itself establish that none of the 573,800 determinants is zero. Accepting the asserted output without an attested execution or an independently supplied exhaustive calculation would assume the principal lower-bound obligation.

Thus the upper bound \(D(77)\le154\) is established, but the supplied record does not affirmatively complete the computational verification needed for \(D(77)\ge152\). The combined interval claim is therefore **indeterminate**, not invalid.

### Dependencies

- **Required declared dependencies:** none.
- The database links are provenance references only. The certificate is reproduced locally, so those mutable external sources are not mathematically necessary for the claim.
