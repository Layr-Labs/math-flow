# Judgment of subject transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`

## Overall assessment

The subject contribution supplies a complete, self-contained proof of the previously missing arbitrary-center rotation-classification lemma. Its main theorem is correct:

> A nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\) must be a half-turn or a quarter-turn.

The application to 153- and 154-point no-three-in-line subsets of \(G_{77}\) is also correct. In particular:

- a 153-point configuration cannot have any nontrivial rotational symmetry;
- any rotationally symmetric 154-point configuration must have the centered half-turn symmetry about \((38,38)\), with the center unselected.

These are structural results only. They neither construct a 153- or 154-point configuration nor rule out such configurations globally, so the certified interval remains

\[
152\le D(77)\le154.
\]

Confidence in the stated rotation results is high. The proof uses no computational or external factual assumptions.

---

## Finding 1: Classification of rotations preserving a finite noncollinear lattice set

**Claim key:** `finite-lattice-sets/nontrivial-rotation-is-half-or-quarter-turn`

### Claim

If \(S\subset\mathbb Z^2\) is finite and noncollinear, and a nonidentity Euclidean rotation \(T\) satisfies \(T(S)=S\), then the rotation angle is \(180^\circ\) or \(\pm90^\circ\). The center of rotation may be arbitrary.

### Judgment

**Accepted as proved.**

### Decisive reasoning

Write the rotation as

\[
T(x)=z+Q(x-z),\qquad
Q=
\begin{pmatrix}
c&-s\\
s&c
\end{pmatrix},
\qquad c^2+s^2=1.
\]

The proof has three essential steps.

#### 1. The rotation matrix has rational entries

Choose noncollinear \(p_0,p_1,p_2\in S\), and form

\[
B=\begin{pmatrix}|&|\\p_1-p_0&p_2-p_0\\|&|\end{pmatrix},
\qquad
C=\begin{pmatrix}|&|\\T(p_1)-T(p_0)&T(p_2)-T(p_0)\\|&|\end{pmatrix}.
\]

Both matrices have integer entries because the original points and their images belong to \(S\subset\mathbb Z^2\). Noncollinearity gives \(\det B\ne0\). Translation by the arbitrary center cancels in differences, so

\[
C=QB,\qquad Q=CB^{-1}.
\]

Since \(B^{-1}\) has rational entries, \(Q\) has rational entries. Therefore

\[
c,s\in\mathbb Q.
\]

This is the key step that makes the conclusion valid even when the rotation does not preserve the whole lattice and its center is not a lattice point.

#### 2. The rotation has finite order

Because \(T\) permutes the finite set \(S\), some positive power \(T^m\) fixes every point of \(S\). It therefore fixes the chosen three noncollinear points. A Euclidean isometry fixing three noncollinear points is the identity, so \(T^m\) is the identity isometry. In particular, \(Q\) has finite order.

This step is logically sufficient; it does not merely show that the restriction of \(T\) to \(S\) has finite order.

#### 3. Rationality excludes all finite rotation orders except \(2\) and \(4\)

Let the eigenvalues of \(Q\) be \(\lambda,\lambda^{-1}\). Since \(Q\) has finite order, they are roots of unity. Thus

\[
\operatorname{tr}(Q)=\lambda+\lambda^{-1}=2c
\]

is an algebraic integer. It is also rational, because \(Q\) is rational. Hence it is an ordinary integer. As \(|2c|\le2\),

\[
2c\in\{-2,-1,0,1,2\}.
\]

The cases are then exhaustive:

- \(2c=2\): \(c=1,s=0\), the identity, which was excluded.
- \(2c=-2\): \(c=-1,s=0\), a half-turn.
- \(2c=0\): \(c=0,s=\pm1\), a quarter-turn in one of the two orientations.
- \(2c=\pm1\): \(c=\pm\frac12\), which would imply
  \[
  s^2=1-c^2=\frac34,
  \]
  so \(s=\pm\frac{\sqrt3}{2}\), contradicting the already established rationality of \(s\).

No possible finite-order rotation remains.

### Scope and assumptions

The noncollinearity hypothesis is essential. For example, a singleton lattice set is preserved by rotations through arbitrary angles about that point. The contribution states the necessary hypothesis explicitly.

The theorem classifies Euclidean rotations only. It does not classify reflections, affine automorphisms, or approximate symmetries.

---

## Finding 2: A 153-point configuration in \(G_{77}\) has no nontrivial rotational symmetry

**Claim key:** `no-three-in-line/g77-153-has-no-nontrivial-rotation`

### Claim

Every 153-point no-three-in-line subset of \(G_{77}\), if one exists, has no nonidentity rotational symmetry about any center.

### Judgment

**Accepted as proved.**

### Decisive reasoning

A 153-point no-three-in-line set is automatically noncollinear, so Finding 1 restricts any nontrivial rotation to a half-turn or quarter-turn.

#### Half-turn exclusion

Under a half-turn, every noncentral point lies in a two-element opposite pair. An invariant finite set of odd cardinality must therefore include the unique fixed point, namely the rotation center \(z\).

If the set contains any other point \(p\), invariance also gives the opposite point \(2z-p\), and

\[
p,\ z,\ 2z-p
\]

are three distinct collinear points. Thus a half-turn-invariant no-three-in-line set of odd size has cardinality at most one. In particular, it cannot have 153 points.

#### Quarter-turn exclusion

Under a quarter-turn, every noncentral orbit has size four. If the center is absent, the cardinality must be divisible by four. Since

\[
153\equiv1\pmod4,
\]

the center would have to be selected.

But quarter-turn invariance also gives half-turn invariance under the square of the rotation. If the center and any noncentral orbit are selected, a point, its half-turn opposite, and the center form a collinear triple. Hence a quarter-turn-invariant no-three-in-line set containing its center can contain no other points.

Therefore a 153-point set admits neither a half-turn nor a quarter-turn. By Finding 1, there is no other possible nontrivial rotation.

### Significance

This is a global symmetry restriction, not a global nonexistence theorem. It shows that any prospective 153-point construction must be rotationally asymmetric, though it may still have reflection symmetry.

---

## Finding 3: Rotational symmetry of a 154-point configuration is necessarily the centered half-turn

**Claim key:** `no-three-in-line/g77-154-rotation-is-centered-half-turn`

### Claim

If a 154-point no-three-in-line subset \(S\subset G_{77}\) has a nontrivial rotational symmetry, then that symmetry is the half-turn about \((38,38)\), and \((38,38)\notin S\).

### Judgment

**Accepted as proved.**

### Decisive reasoning

#### 1. Quarter-turn symmetry is impossible

As above, a quarter-turn-invariant no-three-in-line set either:

- excludes its center and has cardinality divisible by four, or
- contains its center and then has no other selected point.

Since

\[
154\equiv2\pmod4,
\]

a 154-point set cannot be quarter-turn invariant.

By Finding 1, the only remaining nontrivial rotational possibility is a half-turn.

#### 2. Equality in the row and column bounds forces full coordinate range

Each horizontal row contains at most two selected points. There are 77 rows, and

\[
|S|=154=2\cdot77,
\]

so every row contains exactly two points.

The same argument applied to vertical columns shows that every column also contains exactly two points. Consequently every \(x\)-coordinate and every \(y\)-coordinate in \(\{0,\ldots,76\}\) occurs, and the coordinatewise bounding box of \(S\) is

\[
[0,76]\times[0,76].
\]

#### 3. The half-turn center is forced by the bounding box

A half-turn about \(z=(z_x,z_y)\) maps the bounding box of \(S\) to the half-turned bounding box. Since \(S\) is invariant, its bounding box must also be invariant. In one coordinate, the interval \([0,76]\) is sent to

\[
[2z_x-76,\,2z_x].
\]

Equality with \([0,76]\) forces \(2z_x=76\), hence \(z_x=38\). Similarly \(z_y=38\). Thus the center is

\[
z=(38,38).
\]

#### 4. The center is unselected

Under a half-turn, all noncentral orbits have size two and the center is the unique fixed point. An invariant set containing the center therefore has odd cardinality. Since \(154\) is even, the center cannot be selected.

Equivalently, if the center and any noncentral opposite pair were selected, they would form a collinear triple.

### Scope

This does not prove that a 154-point set exists. Nor does it prove that every centered half-turn configuration lies in the much narrower `rct4` class considered in the earlier search contribution. The subject contribution explicitly preserves that distinction.

---

## Finding 4: Effect on the exact-value problem

**Claim key:** `no-three-in-line/d77-exact-value`

### Judgment

**No bound improvement is established.**

The contribution provides neither:

- a 153- or 154-point coordinate certificate,
- an impossibility proof for either cardinality, nor
- a global exhaustive search.

Therefore it does not alter the supplied certified interval

\[
152\le D(77)\le154.
\]

Its mathematical value is instead to constrain the symmetry classes in which any larger configuration could occur:

- cardinality 153: reflection-symmetric or asymmetric only; no rotational symmetry;
- cardinality 154: if rotationally symmetric, necessarily centered half-turn symmetric;
- the asymmetric and reflection-symmetric 154 cases remain possible in principle;
- centered half-turn symmetry is strictly broader than the `rct4` model.

---

## Relationship to the earlier supplied evidence

The preceding `rct4-154-search-instance` contribution stated the same high-level rotational conclusion, but its displayed orbit arguments only handled half-turns and quarter-turns. By themselves, those arguments did not exclude an arbitrary-center rotation of order \(3\), \(5\), \(6\), or another finite order. Thus the earlier conclusion had a genuine missing lemma.

The subject contribution fills that gap correctly by proving that a finite noncollinear lattice set cannot support any of those other rotational orders. This is not a contradiction with the earlier mathematical conclusion; it is a completion of previously insufficient justification.

There is also no conflict with the local-rigidity computation or the baseline 152-point certificate. Those concern existence and local search around a particular configuration, while the present result concerns possible rotational symmetries of hypothetical 153- and 154-point sets.

---

## Missing evidence and limitations

There is no material missing lemma in the proof actually presented. The limitations are matters of scope:

1. **No reflection classification.** Reflection-symmetric configurations are not analyzed.
2. **No existence result.** The proof does not produce a larger configuration.
3. **No nonexistence result.** It does not exclude asymmetric 153- or 154-point sets, reflection-symmetric sets, or general centered-half-turn 154-point sets.
4. **No identification with `rct4`.** Centered half-turn invariance does not imply the anti-diagonal and partial quarter-turn structure of the `rct4` search class.
5. **Repository validation is not mathematical evidence for the theorem.** The listed repository tests may validate file consistency, but the theorem is warranted by the written proof itself.

---

## Contribution and priority

The subject contribution supplies the decisive arbitrary-center finite-rotation argument. The half-turn and quarter-turn orbit-counting arguments and the row/column occupancy observation were already present in the earlier supplied evidence and are repeated self-containedly here. The contribution appropriately does not claim the earlier `rct4` construction methodology or known certificates.

The supplied evidence is not sufficient to adjudicate broader historical priority for the finite-rotation theorem. It is sufficient to recognize that this transaction contains a correct proof of the proposition and closes the explicitly identified logical gap in the earlier rotational classification.
