# Knowledge-Formation Report

## Node: root

**Title:** Research state for maximal-determinant-23  
**Type:** Root  
**Status:** Active

For

\[
D_{23}=\max\left\{|\det A|:A\in\{-1,+1\}^{23\times23}\right\},
\]

the immutable judgments currently support the certified global interval

\[
\boxed{
2{,}779{,}447{,}296{,}000{,}000
\le D_{23}\le
2{,}982{,}295{,}321{,}444{,}352
}.
\]

The lower endpoint is

\[
R=2^{22}\,3\,5^6\,67\,211
 =2{,}779{,}447{,}296{,}000{,}000.
\]

It remains certified by the explicit \(23\times23\) sign-matrix witness assessed in primary judgment

`sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.

That judgment found that the witness reproduces the published record rather than improving it. No supplied judgment exhibits a sign matrix with determinant strictly larger than \(R\).

The supplied real upper estimate is

\[
D_{23}\le
2^{22}\,3\,5^6\,675\sqrt{505}
=
2^{22}\cdot31{,}640{,}625\sqrt{505}.
\]

Primary judgment

`sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`

supports the universal divisibility statement

\[
2^{22}\mid \det A
\]

for every order-\(23\) sign matrix. Hence \(D_{23}/2^{22}\) is an integer, and the exact quotient-level floor

\[
\left\lfloor31{,}640{,}625\sqrt{505}\right\rfloor
=711{,}034{,}613
\]

gives

\[
D_{23}\le
2^{22}\cdot711{,}034{,}613
=
2{,}982{,}295{,}321{,}444{,}352.
\]

The ordinary integer floor of the real endpoint is

\[
2{,}982{,}295{,}321{,}630{,}773,
\]

so divisibility rounding lowers that integer endpoint by \(186{,}421\). The supporting judgment characterizes this only as an arithmetic sharpening of the supplied analytic estimate, not as a stronger analytic inequality.

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

additionally supports a sharply scoped structural exclusion for three-edge star perturbations of order-\(23\) Ehlich block matrices. According to that judgment, the supplied exact verifier:

- canonically enumerates the specified family up to parent-block automorphisms and permutations of the three leaves;
- evaluates candidate determinants using exact rank-two update formulas and exact Bareiss cross-checks;
- reports no candidate at the record square \(R^2\);
- reports \(74{,}896\) canonical candidates strictly above \(R^2\); and
- excludes all of those candidates from being sign-matrix Gram matrices through normalized-square, local quadratic-form, inverse-quadratic, and aggregate cell-moment obstructions.

The judgment treats this as a strong, replayable computational proof for that local family, conditional on successful execution of the supplied verifier. No execution transcript was supplied, so the reported enumeration and exclusion totals remain execution-dependent computational findings rather than totals independently established by the judgment’s prose review.

This structural exclusion does not change either endpoint of the global interval. In particular, the supporting judgment expressly does not infer that all high-determinant order-\(23\) Gram matrices lie in the treated family. It does not cover all perturbation graph shapes, all possible off-diagonal values, or all other candidate Gram families.

The exact value of \(D_{23}\) therefore remains unresolved. The supplied judgments do not:

- prove that the record lower endpoint \(R\) is optimal;
- exhibit a determinant strictly above \(R\);
- prove that the current rounded upper endpoint is attainable;
- exclude the current upper endpoint globally;
- classify all high-determinant order-\(23\) Gram matrices;
- supply a reduction theorem placing every globally relevant Gram matrix in the three-star family; or
- provide an exhaustive search or classification across all remaining candidate families.

The durable research programs directly under the root are:

- `exact-witness-certification` — exact, independently replayable certification of explicit sign-matrix witnesses and their determinants;
- `arithmetic-divisibility-reduction` — reduction of order-\(23\) sign determinants to exact arithmetic divisibility and quotient-level rounding;
- `ehlich-three-star-classification` — exact classification and nonrealizability analysis for three-edge star perturbations of order-\(23\) Ehlich block Gram matrices.

The global interval and the unresolved exact-value question remain at root because they span witness, arithmetic, analytic, classification, and search approaches.

**Provenance**

- Frontier source: William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith, *New lower bounds for the maximal determinant problem* (2003), arXiv:`math/0304410`.
- Record-witness transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- Record-witness judgment: `sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.
- Arithmetic-reduction transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`, ledger position 2.
- Arithmetic-reduction judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Three-star classification transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`, ledger position 3.
- Three-star classification judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- No conflict records or reconciliation judgments were supplied.

## Change: root

The root is revised to register the durable `ehlich-three-star-classification` program and its judgment-supported local structural exclusion. The certified global bounds and unresolved exact-value status are preserved unchanged because the new judgment expressly denies any global interval consequence.

## Node: ehlich-three-star-classification

**Title:** Three-edge star perturbations of order-\(23\) Ehlich block matrices  
**Type:** Program  
**Parent:** `root`  
**Status:** Active

This program studies exact classification and sign-Gram nonrealizability for a finite family derived from order-\(23\) Ehlich block matrices.

For every positive integer partition

\[
r=(r_1,\ldots,r_s),\qquad \sum_i r_i=23,
\]

the parent matrix is

\[
E(r)=20I_{23}-J_{23}
     +4\operatorname{diag}(J_{r_1},\ldots,J_{r_s}).
\]

A family member is obtained by selecting four distinct vertices

\[
(c,\ell_1,\ell_2,\ell_3)
\]

and toggling the three off-diagonal edges between the distinguished center \(c\) and the unordered leaves \(\ell_1,\ell_2,\ell_3\). An edge value changes from \(3\) to \(-1\) when its endpoints lie in the same parent block and from \(-1\) to \(3\) when they lie in different parent blocks.

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

finds the following components mathematically sound:

1. classification up to permutations within parent blocks, permutations of equal-sized parent blocks, and permutations of the three leaves;
2. exact determinant evaluation through the parent inverse and a rank-two symmetric update;
3. exact comparison with the published record square;
4. application of the necessary normalized-square condition for sign Gram matrices;
5. local Hasse-invariant obstructions;
6. inverse-quadratic sign-column enumeration by cell sums; and
7. aggregate cell-moment contradictions certified by integer separating functionals.

The verifier reportedly enumerates:

\[
1{,}255
\]

partitions of \(23\),

\[
1{,}882{,}943
\]

feasible indexed center/leaf-block specifications, and

\[
102{,}799
\]

canonical specifications. It reportedly finds no canonical specification at the record square and \(74{,}896\) strictly above it.

The exact reported exclusion accounting is

\[
74{,}896
=
74{,}792+83+2+19,
\]

where the four terms correspond respectively to:

- nonsquare normalized determinant;
- a local Hasse-invariant obstruction;
- absence of any admissible sign-column pattern satisfying the inverse-quadratic condition; and
- failure of aggregate cell-moment constraints.

On that accounting, the judgment supports the local theorem that no matrix in this precisely specified three-star family is the Gram matrix of an order-\(23\) sign matrix whose determinant reaches or exceeds the published record \(R\).

The judgment qualifies the program’s computational conclusions in several ways:

- the exact numerical totals depend on successful execution of the verifier;
- no execution transcript accompanies the source;
- the orbit-completeness argument relies on the mathematical converse for the canonical descriptor rather than the implemented set-equality diagnostic, which the judgment identifies as tautological;
- the local Hasse detecting primes are recomputed during replay rather than furnished as a standalone transcript; and
- the artifact is an exact conventional Python program, not a formally verified development.

Static inspection found no decisive mathematical error. The judgment describes the source as deterministic, exact, and replayable using only the Python standard library.

This program is local rather than globally exhaustive. It does not classify all order-\(23\) Gram matrices, all three-edge perturbation shapes, perturbations with other off-diagonal values, or every family relevant to the current global upper bound. Its result therefore supplies structural progress without changing the certified interval for \(D_{23}\).

The program’s durable subordinate nodes are:

- `ehlich-three-star-classification/orbit-classification`;
- `ehlich-three-star-classification/exact-determinant-evaluation`;
- `ehlich-three-star-classification/record-threshold-enumeration`;
- `ehlich-three-star-classification/normalized-square-obstruction`;
- `ehlich-three-star-classification/local-quadratic-form-obstruction`;
- `ehlich-three-star-classification/cell-moment-nonfactorization`; and
- `ehlich-three-star-classification/record-level-nonrealizability`.

**Credit carried forward from the judgment**

The judgment preserves attribution of the Ehlich block framework to Ehlich, the record determinant and bound context to Orrick, Solomon, Dowdeswell, and Smith, and the general candidate-Gram and local quadratic-form methodology to prior literature. The preserved judgment text also identifies Robert Raynor with the specific three-star canonicalization and exact enumeration; the supplied attribution text ends at that point, so no broader credit is inferred here.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`, ledger position 3.
- Primary judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Record evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`.
- Arithmetic-divisibility evidence transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`.
- No conflict or reconciliation record applies.

## Change: ehlich-three-star-classification

This new program node is created because the judgment supports a durable, independent agenda of exact Gram-family classification and nonrealizability analysis not covered by the existing witness-certification or arithmetic-divisibility programs.

## Node: ehlich-three-star-classification/orbit-classification

**Title:** Orbit classification of three-star specifications  
**Type:** Classification result  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported with computational qualification

For each positive partition of \(23\), the three-star family selects a distinguished center and three unordered leaves from four distinct vertices of the associated Ehlich block matrix. Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

supports classification up to:

- arbitrary vertex permutations within each parent block;
- permutations of parent blocks having equal size; and
- permutations of the three leaves.

According to the judgment, an orbit is determined by:

- the block sizes occupied by the center and leaves;
- the equality relations specifying which selected vertices occupy the same parent block;
- the distinguished role of the center;
- the unordered status of the leaves; and
- capacity constraints preventing a block from supplying more selected vertices than its size.

The verifier’s canonical descriptor records this information by using first-occurrence labels separately among blocks of each size and minimizing over leaf permutations. Its reconstruction routine selects distinct representative vertices and checks that reconstruction preserves the descriptor. The recursive partition generator covers nondecreasing positive partitions, while combinations with replacement correctly permit repeated leaf-block membership without imposing a leaf order.

The reported classification totals are:

\[
1{,}255
\]

positive partitions of \(23\),

\[
1{,}882{,}943
\]

feasible indexed specifications, and

\[
102{,}799
\]

canonical specifications.

The judgment considers the descriptor method mathematically sound and the totals credible replayable outputs. It nevertheless records two assurance limitations:

1. the exact totals are not independently derived in the prose and require successful execution for confirmation; and
2. the implemented test comparing `set(expanded)` with `set(specs)` is tautological because `specs` is constructed from `expanded`.

Accordingly, completeness rests on the stated converse that two assignments have the same descriptor exactly when they are related by equal-size block permutations and leaf permutations. The judgment says this converse is stated rather than fully proved but appears straightforward from the descriptor’s equality-relation encoding.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Supporting and qualifying judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-ehlich-three-star/orbit-classification`.

## Change: ehlich-three-star-classification/orbit-classification

This node is created to preserve the durable finite-orbit classification method, its reported counts, and the judgment’s explicit caveat that replay and the descriptor converse—not the tautological diagnostic—support completeness.

## Node: ehlich-three-star-classification/exact-determinant-evaluation

**Title:** Exact rank-two determinant evaluation for three-star perturbations  
**Type:** Method and formula  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported

For a partition \(r=(r_1,\ldots,r_s)\) of \(23\), write

\[
H=20I_{23}+4\operatorname{diag}(J_{r_1},\ldots,J_{r_s}),
\qquad
E(r)=H-J.
\]

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

supports the parent determinant formula

\[
\det E(r)
=
20^{23-s}\prod_i(20+4r_i)\,\Delta,
\qquad
\Delta=
1-\sum_i\frac{r_i}{4(5+r_i)}.
\]

For vertices \(x,y\) in parent blocks \(i,j\), respectively, it also supports

\[
(E(r)^{-1})_{xy}
=
\frac{\mathbf 1_{x=y}}{20}
-\frac{\mathbf 1_{i=j}}{20(5+r_i)}
+\frac{1}{16(5+r_i)(5+r_j)\Delta}.
\]

If \(c\) is the center and the three leaf-edge changes are encoded by coefficients \(a_k\), define

\[
v=\sum_{k=1}^3 a_k e_{\ell_k}.
\]

The complete symmetric perturbation is then

\[
e_cv^{\mathsf T}+ve_c^{\mathsf T},
\]

which has rank at most two. The supported determinant correction is

\[
\det\!\left(E+e_cv^{\mathsf T}+ve_c^{\mathsf T}\right)
=
\det(E)
\left[
(1+e_c^{\mathsf T}E^{-1}v)^2
-
(e_c^{\mathsf T}E^{-1}e_c)
(v^{\mathsf T}E^{-1}v)
\right].
\]

The verifier implements these calculations with exact rational arithmetic. For the relevant normalized-square survivors, it reconstructs the full \(23\times23\) integer matrix and recomputes its determinant by fraction-free Bareiss elimination. The judgment regards this direct reconstruction as a material arithmetic cross-check of the rank-two formula.

No floating-point determinant is used.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Supporting judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-ehlich-three-star/rank-two-determinant-formula`.

## Change: ehlich-three-star-classification/exact-determinant-evaluation

This node is created to retain the exact parent formulas, rank-two update method, and independent Bareiss cross-check as a reusable computational method within the program.

## Node: ehlich-three-star-classification/record-threshold-enumeration

**Title:** Exact enumeration at and above the published record square  
**Type:** Computational classification result  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported conditional on replay

Let

\[
R=2^{22}\,3\,5^6\,67\,211.
\]

For a sign matrix \(A\) with Gram matrix \(G=AA^{\mathsf T}\),

\[
\det G=(\det A)^2.
\]

Thus any member of the three-star family capable of supporting

\[
|\det A|\ge R
\]

must satisfy

\[
\det G\ge R^2.
\]

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

supports the threshold arithmetic used by the verifier:

\[
3\cdot5^6\cdot67\cdot211=662{,}671{,}875,
\]

and hence

\[
R^2=
\left(2^{22}\cdot662{,}671{,}875\right)^2.
\]

Across the reportedly \(102{,}799\) canonical specifications, the deterministic exact verifier reports:

- no specification with determinant exactly \(R^2\); and
- \(74{,}896\) specifications with determinant strictly greater than \(R^2\).

Candidates below \(R^2\) are irrelevant to the stated local record-level exclusion and are not claimed to be nonrealizable by that theorem.

The verifier compares exact integer determinants and contains no random or heuristic step. The judgment supports the threshold logic and regards the enumeration as a valid replayable certificate design. It qualifies the numerical totals as execution-dependent because static source inspection cannot itself confirm all generated cases and no execution transcript was supplied.

The verifier also requires the candidate determinants to be divisible by \(2^{44}\). The judgment finds this consistent with the family’s entries: the diagonal \(23\) and off-diagonal entries \(3\) and \(-1\) are all congruent to \(-1\pmod 4\), allowing \(22\) row differences to contribute the factor \(4^{22}=2^{44}\).

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Record evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`.
- Supporting and qualifying judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-ehlich-three-star/record-threshold-enumeration`.

## Change: ehlich-three-star-classification/record-threshold-enumeration

This node is created to preserve the exact record-square comparison and reported finite counts while making their dependence on successful verifier execution explicit.

## Node: ehlich-three-star-classification/normalized-square-obstruction

**Title:** Normalized determinant square obstruction in the three-star family  
**Type:** Nonrealizability criterion and result  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported with replay-dependent count

For every order-\(23\) sign matrix \(A\), the previously supported universal divisibility result gives

\[
2^{22}\mid\det A.
\]

Consequently, if a candidate matrix \(G\) is a sign Gram matrix,

\[
G=AA^{\mathsf T},
\]

then

\[
\frac{\det G}{2^{44}}
=
\left(\frac{\det A}{2^{22}}\right)^2
\]

must be an integer square.

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

finds that the verifier applies this necessary condition correctly. It computes the normalized quotient exactly, applies integer square root, and verifies the result by squaring.

Of the reportedly \(74{,}896\) canonical three-star specifications strictly above the record square, the verifier reports that

\[
74{,}792
\]

have nonsquare normalized determinant. Subject to successful replay of the enumeration, each of these candidates is conclusively incompatible with an order-\(23\) sign-matrix Gram factorization.

The mathematical criterion is supported without qualification. The count \(74{,}792\) remains dependent on successful execution of the exact verifier.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Divisibility evidence transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`.
- Divisibility judgment: `sha256:f6722db5b0fa49f20e948a0e36f8aaa83d1aaf1700db4823dd0b20df5aaddbe3`.
- Supporting three-star judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-sign-gram/normalized-determinant-square-condition`.

## Change: ehlich-three-star-classification/normalized-square-obstruction

This node is created to record the program-specific application of the established \(2^{22}\)-divisibility theorem and the resulting first-stage exclusion count, without altering the broader arithmetic program.

## Node: ehlich-three-star-classification/local-quadratic-form-obstruction

**Title:** Local Hasse-invariant obstruction for normalized-square candidates  
**Type:** Nonrealizability criterion and result  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported with replay-dependent count

If a nonsingular rational matrix \(G\) has a sign-matrix Gram factorization

\[
G=AA^{\mathsf T},
\]

then over \(\mathbb Q\),

\[
G=A I_{23}A^{\mathsf T}.
\]

It is therefore rationally congruent to the identity quadratic form. Matching local Hasse invariants is a necessary condition, and the identity form has local Hasse invariant \(+1\). A prime \(p\) for which

\[
\epsilon_p(G)=-1
\]

conclusively rules out the proposed Gram factorization.

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

supports the verifier’s exact implementation. According to the judgment, it:

1. reconstructs the full candidate matrix;
2. diagonalizes the associated form through exact rational Schur complements;
3. independently obtains the same diagonal pivots from ratios of exact leading principal minors;
4. verifies that the pivot product equals the determinant;
5. evaluates standard odd-prime and \(2\)-adic Hilbert-symbol formulas; and
6. searches relevant prime divisors until it finds a local invariant of \(-1\).

Of the reportedly \(104\) above-threshold candidates that survive the normalized-square test, the verifier reports local obstructions for

\[
83.
\]

The judgment finds both the rational-congruence argument and the implementation mathematically valid. The count of \(83\) and the associated detecting primes are replay-dependent: the primes are recomputed during execution rather than supplied in a separate certificate transcript.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Supporting and qualifying judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-ehlich-three-star/local-quadratic-form-obstruction`.

## Change: ehlich-three-star-classification/local-quadratic-form-obstruction

This node is created to retain the local quadratic-form criterion, its exact verification design, and the judgment’s qualification that the candidate count and detecting primes must be reproduced by execution.

## Node: ehlich-three-star-classification/cell-moment-nonfactorization

**Title:** Inverse-quadratic and aggregate cell-moment nonfactorization  
**Type:** Nonrealizability criterion and result  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported with replay-dependent accounting

If

\[
G=AA^{\mathsf T}
\]

and \(x\) is a column of the nonsingular sign matrix \(A\), then the necessary inverse-quadratic condition is

\[
x^{\mathsf T}G^{-1}x=1.
\]

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

supports the verifier’s reduction of this condition to a finite enumeration by cell sums.

The cells consist of:

- singleton cells for the center and the three leaves; and
- one residual cell for the unselected vertices of each nonempty parent block.

The verifier checks the required cell constancy of both \(G\) and \(G^{-1}\). Consequently, the quadratic value depends only on

\[
t_i=\sum_{a\in C_i}x_a.
\]

For a cell of size \(m\), every possible sign sum is included through

\[
-m,-m+2,\ldots,m.
\]

The judgment finds that the implemented quadratic formula correctly includes the fixed diagonal terms, the within-cell \(t_i^2\) terms, and twice the between-cell \(t_it_j\) terms.

Among the final \(21\) reported normalized-square candidates not excluded by local Hasse invariants:

- \(2\) reportedly admit no sign-column pattern satisfying \(x^{\mathsf T}G^{-1}x=1\);
- \(19\) reportedly admit individual patterns but fail the necessary aggregate cell moments.

For hypothetical columns \(x^{(1)},\ldots,x^{(23)}\), those moments must satisfy

\[
\sum_{k=1}^{23}t_i^{(k)}t_j^{(k)}
=
\sum_{a\in C_i}\sum_{b\in C_j}G_{ab}.
\]

For each of the \(19\) remaining cases, the supplied certificates give an integer linear functional that is nonnegative on every individually admissible pattern but strictly negative on the required aggregate target. The judgment accepts these as valid finite Farkas-type contradictions.

The verifier reconstructs all admissible patterns and checks the functional inequalities with exact integers rather than trusting an external linear-programming solver. It also reportedly verifies distinctness and complete accounting of the final square candidates.

The judgment finds no logical gap in these criteria or in the certificate-checking design. The split into \(2\) and \(19\), like the other family totals, remains conditional on successful replay.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Supporting judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-ehlich-three-star/cell-moment-nonfactorization`.

## Change: ehlich-three-star-classification/cell-moment-nonfactorization

This node is created to preserve the final-stage inverse-quadratic and aggregate-moment obstructions, including the exact separating-certificate logic and the execution qualification on their reported accounting.

## Node: ehlich-three-star-classification/record-level-nonrealizability

**Title:** Record-level nonrealizability of the three-star family  
**Type:** Local exclusion theorem  
**Parent:** `ehlich-three-star-classification`  
**Status:** Supported conditional on replay

Let

\[
R=2^{22}\,3\,5^6\,67\,211
\]

be the published order-\(23\) record determinant.

Primary judgment

`sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`

supports the following local conclusion, conditional on successful replay of the supplied exact classification and counts:

> No three-edge star perturbation of an order-\(23\) Ehlich block matrix in the precisely specified family is the Gram matrix of an order-\(23\) sign matrix \(A\) satisfying \(|\det A|\ge R\).

The supporting accounting is:

- reportedly no canonical specification has determinant \(R^2\);
- reportedly \(74{,}896\) canonical specifications have determinant greater than \(R^2\); and
- all \(74{,}896\) are excluded through the exact partition

\[
74{,}896
=
74{,}792+83+2+19.
\]

The categories are:

1. \(74{,}792\) with nonsquare normalized determinant;
2. \(83\) with a local Hasse-invariant obstruction;
3. \(2\) with no admissible sign-column pattern under the inverse-quadratic condition; and
4. \(19\) contradicted by aggregate cell-moment separating functionals.

The judgment characterizes this as a proof of nonrealizability for the stated family rather than a heuristic non-finding. Its assurance remains conditional on execution because no verifier-run transcript is supplied and the artifact is not formally verified.

This theorem has no certified global numerical consequence for \(D_{23}\). The judgment expressly states that the artifact does not:

- prove that every high-determinant Gram matrix belongs to an Ehlich block perturbation family;
- cover all three-edge perturbation graph shapes;
- cover off-diagonal values other than \(3\) and \(-1\);
- classify all other candidate Gram families;
- lower the current global upper bound;
- improve the record lower bound; or
- determine \(D_{23}\).

A global consequence would require an additional reduction theorem or exhaustive treatment of the remaining candidate families, neither of which is supplied.

**Provenance**

- Subject transaction: `f9b8f29c397afc84ab9a8fdeb1d3d07d32b5a6d5`.
- Record evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`.
- Divisibility evidence transaction: `7b28860c418486cb41e6379e68cc355ff861b1a5`.
- Supporting and qualifying judgment: `sha256:270a5cfb09d5e967f5ef4bcaf8f7cc659eed00bcf50a2f1148124f4b135fdc1e`.
- Claim key: `order-23-ehlich-three-star/record-level-nonrealizability`.
- Global-scope qualification: claim key `order-23-maxdet/global-interval-consequence`.

## Change: ehlich-three-star-classification/record-level-nonrealizability

This node is created to materialize the combined local exclusion theorem separately from its component methods while preserving the judgment’s replay condition and its explicit denial of any improvement to the global interval.
