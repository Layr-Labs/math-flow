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

