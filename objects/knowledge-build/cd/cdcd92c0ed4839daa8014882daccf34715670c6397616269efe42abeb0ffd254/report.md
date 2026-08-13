# Knowledge-Formation Report

## Node: no-three-in-line/d77-exact-value

- **Type:** Central question and global bounds
- **Title:** Exact value and certified interval for \(D(77)\)
- **Status:** Active and unresolved
- **Parent:** `root`
- **Lineage:** None

The central question is to determine the largest cardinality \(D(77)\) of a no-three-in-line subset of

\[
G_{77}=\{0,1,\ldots,76\}^2.
\]

The accepted primary judgments support the current certified interval

\[
\boxed{152\le D(77)\le154}.
\]

They do not select among

\[
D(77)=152,\qquad D(77)=153,\qquad D(77)=154.
\]

### Certified lower bound

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` accepts an exact, self-contained computational certificate for 152 distinct points in \(G_{76}\) with no three collinear. Since

\[
G_{76}\subset G_{77},
\]

the same configuration establishes

\[
D(77)\ge152.
\]

Primary judgment `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a` separately accepts the same implication from a republished executable package. That package re-verifies the existing bound rather than improving it. Its evidence does not establish a completed governed hosted run, and its checker is not algorithmically independent of the earlier verifier; these qualifications do not alter the certified lower bound.

### Certified upper bound

Primary judgment `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e` accepts the elementary row-capacity argument. Each of the 77 horizontal grid lines contains at most two selected points, so

\[
D(77)\le2\cdot77=154.
\]

The corresponding column argument gives the same capacity.

### Necessary occupancy restrictions

The accepted judgments support the following necessary conditions:

- a hypothetical 154-point set must contain exactly two points in every row and exactly two points in every column;
- a hypothetical 153-point set must contain two points in 76 rows and one point in the remaining row, and likewise two points in 76 columns and one point in the remaining column.

These are necessary conditions only. They establish neither existence nor nonexistence at either cardinality.

### Rotational restrictions

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts a classification of nonidentity rotations preserving finite noncollinear lattice sets and its consequences at the two unresolved cardinalities:

- every hypothetical 153-point configuration has no nonidentity rotational symmetry about any center;
- if a hypothetical 154-point configuration has nontrivial rotational symmetry, it must have the half-turn about \((38,38)\);
- the center \((38,38)\) must then be unselected;
- reflection-symmetric and asymmetric configurations remain possible in principle; and
- general centered-half-turn symmetry is strictly broader than the `rct4` class.

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` additionally accepts the elementary half-turn and quarter-turn orbit obstructions and the centered-half-turn conclusion for cardinality 154. That judgment qualifies the broader rotational-classification argument in its subject transaction because the written argument there omitted the arbitrary-center lattice-rotation classification. This does not overturn the existing rotational conclusions, because the missing classification had already been accepted from the earlier subject and judgment.

### Local rigidity around the certified 152-point record

Primary judgment `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927` accepts a local restriction around eight specified embeddings of one certified 152-point \(G_{76}\) record:

- none of those embeddings can be improved after removing at most two embedded points;
- for each specified embedding \(E\), any no-three-in-line set \(S\) with \(|S|\ge153\) must satisfy
  \[
  |E\setminus S|\ge3,\qquad |S\setminus E|\ge4,\qquad |E\triangle S|\ge7;
  \]
- configurations based on three or more removals remain unexamined; and
- other 152-point configurations, and larger configurations sufficiently far from every specified embedding, remain unconstrained by that computation.

This is a local rigidity result, not a global impossibility theorem.

### Exact `rct4` search model

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts with high confidence from static inspection that the supplied \(n=77\) model is sound and complete for a specified 154-point `rct4` subclass. That subclass imposes more than centered-half-turn symmetry:

- the anti-diagonal is empty;
- off the two diagonals, selected cells occur in complete quarter-turn orbits; and
- exactly one half-turn pair on the main diagonal is selected.

The judgment accepts the model’s orbit counts, primitive-line enumeration, weighted line constraints, CNF translation, and deterministic statistics within that restricted class.

The associated bounded solver runs do not resolve the model. They returned `UNKNOWN` outcomes or timeouts and supplied no proof trace establishing infeasibility. Comparable failures at known satisfiable calibration sizes prevent those timeouts from carrying negative mathematical force.

The implications remain precisely scoped:

- a feasible \(n=77\) assignment would provide a 154-point configuration and establish \(D(77)=154\);
- an infeasibility proof for this model would exclude only the `rct4` subclass;
- it would not exclude general centered-half-turn configurations, reflection-symmetric configurations, or asymmetric configurations.

### Unresolved scope

No accepted contribution supplies:

- a 153- or 154-point coordinate certificate;
- a global impossibility proof for either cardinality;
- a completed exhaustive search resolving the interval; or
- an upper-bound argument improving \(D(77)\le154\).

The accepted certificate, occupancy restrictions, symmetry theorems, local-rigidity computation, and restricted `rct4` model therefore leave the exact value unresolved.

### Authoritative provenance

- Baseline certificate, bounds, occupancy, and unresolved-status judgment: `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- Baseline subject transaction: `dfc0cc40d41105292a119840dcdbe6f22860cf43`, ledger position 1
- Embedded-record rigidity judgment: `sha256:71fbde8d269728a92be52f6401e857230043ee6938c45f810c32308d88fb9927`
- Rigidity subject transaction: `c5e8096d942d57228bb4fed00f7617fb6b43af9f`, ledger position 2
- Rotational-classification judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Rotational subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`, ledger position 4
- Republishing judgment: `sha256:8c5f8eeb55af54b575fd3d46473e7894095afd6a4741186fe0583d3d0feade8a`
- Republishing subject transaction: `0ffe9a12c3ad44cf136dd22df7083dcdd53af1b0`, ledger position 5
- `rct4` model and bounded-search judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- `rct4` subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: no-three-in-line/d77-exact-value

Updated the central question to incorporate the accepted restricted `rct4` model, its unresolved solver status, and the latest symmetry evidence while preserving the unchanged certified interval and all previously accepted qualifications.

## Node: programs/rotational-symmetry

- **Type:** Research program
- **Title:** Rotational symmetry of finite lattice configurations
- **Status:** Active
- **Parent:** `root`
- **Lineage:** None; this program was not formed by a split or merge.

This program organizes accepted results about rotations preserving finite noncollinear lattice sets and the consequences of those results for hypothetical 153- and 154-point no-three-in-line configurations in \(G_{77}\).

Its accepted structural knowledge consists of:

- the classification that a nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\) must be a half-turn or quarter-turn, even when its center is arbitrary;
- the obstruction showing that an odd-cardinality no-three-in-line set invariant under a half-turn has at most one point;
- the obstruction showing that a quarter-turn-invariant no-three-in-line set has cardinality divisible by four or equal to one;
- the resulting exclusion of every nonidentity rotational symmetry for a hypothetical 153-point configuration;
- the conclusion that a rotationally symmetric hypothetical 154-point configuration must be invariant under the half-turn about \((38,38)\), with that center unselected; and
- the distinction between general centered-half-turn configurations and the stricter `rct4` subclass.

The program now includes a durable computational subprogram for exact modeling and search within the `rct4` subclass. That subprogram records model equivalence, implementation calibration, and the unresolved satisfiability status of the \(n=77\) instance.

The program does not currently classify reflections, affine automorphisms, or approximate symmetries. It does not establish the existence or nonexistence of 153- or 154-point configurations.

### Active structure

Direct structural descendants include:

- `finite-lattice-sets/nontrivial-rotation-is-half-or-quarter-turn`
- `no-three-in-line/odd-cardinality-half-turn-obstruction`
- `no-three-in-line/quarter-turn-cardinality-obstruction`
- `no-three-in-line/g77-153-has-no-nontrivial-rotation`
- `no-three-in-line/g77-154-rotation-is-centered-half-turn`

Nested computational program:

- `programs/rotational-symmetry/rct4-search`

### Authoritative provenance

- General rotation-classification judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Classification subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`, ledger position 4
- Orbit-obstruction and `rct4` model judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Associated subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: programs/rotational-symmetry

Updated the program to organize the newly accepted half-turn and quarter-turn obstruction lemmas and to add a separately extensible nested agenda for exact `rct4` modeling and search.

## Node: no-three-in-line/odd-cardinality-half-turn-obstruction

- **Type:** Structural lemma
- **Title:** Odd-cardinality obstruction to half-turn symmetry
- **Status:** Accepted
- **Parent:** `programs/rotational-symmetry`
- **Lineage:** None

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts the following statement:

> If a finite no-three-in-line set \(S\) is invariant under the half-turn
> \[
> p\longmapsto 2z-p
> \]
> about a point \(z\) and \(|S|\) is odd, then \(|S|\le1\).

The judgment accepts the orbit and midpoint reasoning given in its subject evidence: odd cardinality forces the half-turn center to be the fixed selected point, while any noncentral orbit would form a forbidden collinear triple with that center.

The conclusion applies to a half-turn about any center; the center need not initially be assumed to be a grid point. In particular, it excludes half-turn symmetry for every hypothetical 153-point no-three-in-line subset of \(G_{77}\).

This lemma does not exclude quarter-turns or other rotational orders by itself, and it does not prove the nonexistence of 153-point configurations.

### Authoritative provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Claim key: `no-three-in-line/odd-cardinality-half-turn-obstruction`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: no-three-in-line/odd-cardinality-half-turn-obstruction

Created a durable structural lemma for the accepted odd-cardinality half-turn obstruction, which is independently useful beyond the particular 153-point application.

## Node: no-three-in-line/quarter-turn-cardinality-obstruction

- **Type:** Structural lemma
- **Title:** Cardinality obstruction to quarter-turn symmetry
- **Status:** Accepted
- **Parent:** `programs/rotational-symmetry`
- **Lineage:** None

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts the following statement:

> A no-three-in-line set invariant under a quarter-turn has cardinality divisible by four or has cardinality one.

The judgment accepts the orbit analysis supplied in its evidence:

- every noncentral quarter-turn orbit has size four;
- if the center is unselected, the set is a union of four-element orbits;
- if the center is selected, the associated half-turn and midpoint obstruction prevents any other point from being selected.

Consequently, quarter-turn symmetry is impossible at both unresolved upper-end cardinalities:

\[
153\equiv1\pmod4,\qquad 154\equiv2\pmod4,
\]

with the cardinality-one exception irrelevant to either case.

This lemma does not classify every possible finite-order lattice rotation by itself and does not establish the existence or nonexistence of 153- or 154-point configurations.

### Authoritative provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Claim key: `no-three-in-line/quarter-turn-cardinality-obstruction`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: no-three-in-line/quarter-turn-cardinality-obstruction

Created a durable structural lemma for the accepted quarter-turn orbit obstruction and its applications at cardinalities 153 and 154.

## Node: no-three-in-line/g77-153-has-no-nontrivial-rotation

- **Type:** Structural theorem
- **Title:** Rotational asymmetry of any 153-point configuration in \(G_{77}\)
- **Status:** Accepted as proved
- **Parent:** `programs/rotational-symmetry`
- **Lineage:** None

The accepted judgments support the conclusion that every 153-point no-three-in-line subset of \(G_{77}\), if such a subset exists, has no nonidentity rotational symmetry about any center.

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the general finite-lattice rotation classification needed to reduce arbitrary-center rotations to half-turns and quarter-turns.

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` separately accepts:

- the odd-cardinality half-turn obstruction, excluding half-turn symmetry at cardinality 153; and
- the quarter-turn cardinality obstruction, excluding quarter-turn symmetry at cardinality 153.

The later judgment qualifies the broader rotational-classification argument in its own subject transaction because that written argument did not explicitly exclude other finite-order lattice rotations about arbitrary centers. It does not reject the theorem. The missing classification step is supplied by the earlier accepted classification judgment.

This theorem is only a symmetry restriction:

- it does not prove that a 153-point configuration is impossible;
- reflection symmetry remains possible in principle;
- asymmetric configurations remain possible in principle; and
- it does not improve the certified interval for \(D(77)\).

### Credit carried from the judgments

The earlier judgment records that half-turn and quarter-turn orbit arguments were already present in earlier supplied evidence, while its subject supplied the arbitrary-center rotation classification. The later judgment accepts a self-contained presentation of the elementary orbit obstructions but does not replace the earlier source of the general classification.

### Authoritative provenance

- General rotational-classification judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Classification subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`, ledger position 4
- Half-turn and quarter-turn obstruction judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Obstruction subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3
- Claim key: `no-three-in-line/g77-153-has-no-nontrivial-rotation`

## Change: no-three-in-line/g77-153-has-no-nontrivial-rotation

Updated provenance to incorporate the newly accepted half-turn and quarter-turn obstructions while preserving the earlier judgment as the source of the arbitrary-center rotation classification required for the full theorem.

## Node: no-three-in-line/g77-154-rotation-is-centered-half-turn

- **Type:** Structural theorem
- **Title:** Rotational symmetry of a 154-point configuration in \(G_{77}\)
- **Status:** Accepted as proved
- **Parent:** `programs/rotational-symmetry`
- **Lineage:** None

The accepted judgments support the following conditional conclusion:

> If a 154-point no-three-in-line subset \(S\subset G_{77}\) has a nonidentity rotational symmetry, then that symmetry is the half-turn about \((38,38)\), and \((38,38)\notin S\).

Primary judgment `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca` accepts the arbitrary-center finite-lattice rotation classification that reduces possible nonidentity rotations to half-turns and quarter-turns.

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts:

- the exclusion of quarter-turn symmetry at cardinality 154;
- the row and column saturation argument for a 154-point set;
- the resulting coordinate extrema \([0,76]\) in both coordinates;
- the conclusion that a preserving half-turn must have center \((38,38)\); and
- the conclusion that this center is unselected.

The later judgment qualifies the broad rotational wording in its subject evidence because that presentation omitted the arbitrary-center classification step. The accepted theorem remains supported by the earlier judgment that supplied this missing classification.

The conclusion is conditional and has strict scope:

- it does not establish that a 154-point configuration exists;
- it does not exclude asymmetric 154-point configurations;
- it does not exclude reflection-symmetric 154-point configurations;
- it does not imply that every centered-half-turn configuration belongs to `rct4`; and
- the `rct4` class is a strict subclass imposing additional diagonal and quarter-turn-orbit conditions.

### Credit carried from the judgments

The earlier judgment records that half-turn and quarter-turn orbit counting and row/column occupancy observations were already present in earlier supplied evidence, while its subject supplied the missing arbitrary-center classification. The later judgment accepts the elementary obstruction and centering arguments in its subject but does not establish that the narrower `rct4` model exhausts centered-half-turn configurations.

### Authoritative provenance

- General rotational-classification judgment: `sha256:21f3e6bb405eaaf804b58020a1695c213023b0dd3f1d25a08248fb5a48750eca`
- Classification subject transaction: `29ccbd396781fd36d436ed2e6d0952a4730361b9`, ledger position 4
- Centering and orbit-obstruction judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Associated subject transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3
- Represented claim keys:
  - `no-three-in-line/g77-154-rotation-is-centered-half-turn`
  - `no-three-in-line/d77-154-half-turn-center`

## Change: no-three-in-line/g77-154-rotation-is-centered-half-turn

Updated the theorem’s provenance and scope to include the newly accepted centering argument and to preserve the judged distinction between general centered-half-turn symmetry and the stricter `rct4` subclass.

## Node: programs/rotational-symmetry/rct4-search

- **Type:** Research subprogram
- **Title:** Exact modeling and search in the `rct4` symmetry class
- **Status:** Active
- **Parent:** `programs/rotational-symmetry`
- **Lineage:** None; this subprogram was not formed by a split or merge.

This subprogram organizes exact encodings, validation methods, calibration certificates, and satisfiability searches for the `rct4` class of no-three-in-line configurations.

For odd grid size \(n\), the modeled class uses the quarter-turn

\[
\rho(i,j)=(j,n-1-i)
\]

and imposes the following pattern:

1. the anti-diagonal is empty;
2. selected off-diagonal cells occur in complete quarter-turn orbits;
3. exactly one half-turn pair on the main diagonal is selected.

At \(n=77\), these conditions define a restricted class of 154-point configurations. Every member has centered-half-turn symmetry, but not every centered-half-turn configuration satisfies the additional `rct4` conditions. The subprogram therefore investigates one strict subclass of the remaining rotationally symmetric route rather than all possible 154-point sets.

Its accepted current knowledge is:

- the supplied \(n=77\) constraint model exactly encodes the stated 154-point `rct4` subclass;
- five committed certificates at \(n=41,47,57,65,69\) provide exact regression checks at those sizes;
- the \(n=77\) instance remains unresolved because the reported runs returned only `UNKNOWN` outcomes or timeouts;
- those timeouts have no negative mathematical implication; and
- a feasible \(n=77\) assignment would establish \(D(77)=154\), whereas an infeasibility proof would exclude only this subclass.

### Active descendants

- `no-three-in-line/d77-rct4-154-model-equivalence`
- `no-three-in-line/rct4-model-calibration-certificates`
- `no-three-in-line/d77-rct4-154-satisfiability`

### Credit carried from the judgment

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` attributes the new symmetry observations, \(n=77\) implementation, validation machinery, and bounded search report to Robert Raynor and the disclosed AI research agent. It also records that the contribution attributes the underlying `rct4` class and symmetry-reduction method to Thomas; the supplied immutable judgment text ends at that first name, so no further attribution is added here.

### Authoritative provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: programs/rotational-symmetry/rct4-search

Created a nested research program because exact `rct4` modeling, calibration, and satisfiability search form a coherent, separately extensible agenda within the broader rotational-symmetry program.

## Node: no-three-in-line/d77-rct4-154-model-equivalence

- **Type:** Computational model theorem
- **Title:** Exact equivalence of the \(n=77\) model and the 154-point `rct4` subclass
- **Status:** Accepted with high confidence from static inspection
- **Parent:** `programs/rotational-symmetry/rct4-search`
- **Lineage:** None

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts that feasible assignments of the supplied \(n=77\) model correspond exactly to 154-point no-three-in-line configurations satisfying the stated `rct4` pattern:

1. the anti-diagonal is empty;
2. occupied cells away from the two diagonals form complete quarter-turn orbits;
3. exactly one half-turn pair on the main diagonal is occupied.

### Orbit structure and cardinality

For \(n=77\), removing the main and anti-diagonals leaves

\[
77^2-(2\cdot77-1)=5776
\]

cells. The judgment accepts that these form 1444 quarter-turn orbits of size four. The noncentral main-diagonal points form 38 half-turn pairs.

The model imposes

\[
\sum y_{\mathrm{off}}=38,\qquad \sum y_{\mathrm{diag}}=1,
\]

so every feasible assignment selects

\[
4\cdot38+2=154
\]

points. The implementation treats the center \((38,38)\) as part of the empty anti-diagonal and does not assign it a main-diagonal variable.

### Exact line constraints

The judgment accepts the supplied primitive-direction enumeration as complete for lattice lines capable of containing a collinear triple. Each maximal grid line is represented once, and each orbit variable receives as coefficient the number of its selected cells lying on that line.

Thus every weighted inequality

\[
\sum_v c_vy_v\le2
\]

expresses that the corresponding line contains at most two selected cells. Lines whose total possible coefficient is at most two may be discarded as tautological, and deduplicating identical weighted inequalities does not change the feasible set.

The judgment therefore accepts both directions of the model equivalence:

- every feasible assignment yields a 154-point no-three-in-line set in the specified `rct4` class;
- every 154-point no-three-in-line set in that class induces a feasible assignment.

### CNF translation and deterministic statistics

The judgment accepts the CNF treatment of weighted at-most-two constraints, including the handling of variables with coefficients one, two, or at least three. Exact-cardinality constraints are delegated to PySAT’s standard cardinality encoder.

The program deterministically regenerates and compares the reported \(n=77\) statistics:

- 1444 off-diagonal orbit variables;
- 38 main-diagonal pair variables;
- 388,148 deduplicated line constraints.

The variable counts also follow from the accepted orbit calculation. The exact line-constraint count remains a computational census generated by the supplied exact-integer program rather than a separately hand-derived theorem.

### Scope

This node establishes model equivalence only. It does not establish that the model is satisfiable or unsatisfiable. The modeled class is a strict subclass of centered-half-turn configurations and does not cover reflection-symmetric or asymmetric 154-point sets.

### Authoritative provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Claim key: `no-three-in-line/d77-rct4-154-model-equivalence`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: no-three-in-line/d77-rct4-154-model-equivalence

Created a stable computational-model node for the accepted soundness and completeness of the \(n=77\) encoding within the precisely stated `rct4` subclass.

## Node: no-three-in-line/rct4-model-calibration-certificates

- **Type:** Computational validation result
- **Title:** Exact calibration certificates for the `rct4` model
- **Status:** Accepted within the five committed sizes
- **Parent:** `programs/rotational-symmetry/rct4-search`
- **Lineage:** None

Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` accepts the five committed certificates at

\[
n=41,47,57,65,69
\]

as exact implementation regression checks for the supplied `rct4` model at those sizes.

For each certificate, the supplied program:

1. decodes two points per row;
2. checks distinctness and grid membership;
3. checks every point triple using an exact determinant;
4. checks the empty anti-diagonal condition and the required orbit structure; and
5. checks the induced assignment against all generated model constraints.

The judgment accepts these checks as meaningful exact validation at the five listed sizes. The certificate payload forces \(2n\) decoded points, and the orbit-count checks ensure the intended treatment of the selected main-diagonal pair in those cases.

The accepted scope is limited:

- the certificates validate the implementation on these five instances;
- they do not prove a historical claim covering an entire range of odd grid sizes;
- file hashes establish identity of the supplied files, not external provenance or discovery priority; and
- satisfiability at these smaller sizes does not establish satisfiability at \(n=77\).

The comparable solver failures reported at \(n=41\) and \(n=47\), despite these committed satisfying certificates, also serve as accepted evidence that analogous timeouts at \(n=77\) have no negative mathematical force.

### Authoritative provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Claim key: `no-three-in-line/rct4-model-calibration-certificates`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: no-three-in-line/rct4-model-calibration-certificates

Created a stable validation node for the five accepted exact regression certificates while preserving the judgment’s limitations on historical range, provenance, and extrapolation to \(n=77\).

## Node: no-three-in-line/d77-rct4-154-satisfiability

- **Type:** Restricted exact question and computational status
- **Title:** Satisfiability of the \(n=77\) 154-point `rct4` instance
- **Status:** Active and unresolved
- **Parent:** `programs/rotational-symmetry/rct4-search`
- **Lineage:** None

The exact question is whether the accepted \(n=77\) `rct4` model has a feasible assignment. Primary judgment `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5` finds that the supplied evidence establishes neither satisfiability nor unsatisfiability.

The reported CP-SAT runs ended with `UNKNOWN` outcomes, and the reported SAT runs ended in timeouts. No solver returned a certified infeasibility result. No coordinate certificate, committed solver log, proof trace, or exact committed CaDiCaL invocation resolves the instance.

The same pipeline reportedly failed within comparable budgets at \(n=41\) and \(n=47\), where committed certificates show that the corresponding instances are satisfiable. The judgment therefore assigns the \(n=77\) timeout behavior no negative mathematical force.

The current implications are limited to:

- a feasible assignment would give a 154-point no-three-in-line subset of \(G_{77}\), proving \(D(77)=154\);
- a certified infeasibility result would exclude only the `rct4` subclass;
- infeasibility would not exclude all centered-half-turn configurations;
- it would not exclude reflection-symmetric or asymmetric 154-point configurations; and
- the present timeouts imply none of these outcomes.

The private-channel “breakthrough report” mentioned in the judgment carries no mathematical weight because it supplies no definite value, coordinate certificate, proof, or solver output.

This is an unresolved restricted decision problem, not an active conflict between opposed judgments.

### Authoritative provenance

- Primary judgment: `sha256:d24a70c16a08ff85401e969cfe12d8f8253056bb8d75e469ec226eba7a3b44c5`
- Claim key: `no-three-in-line/d77-rct4-154-satisfiability`
- Subject and evidence transaction: `c98dd877ad81611a9a469b1bd790cd909b56b1ce`, ledger position 3

## Change: no-three-in-line/d77-rct4-154-satisfiability

Created a durable restricted question node to preserve the judged `UNKNOWN` status and prevent bounded timeouts from being conflated with an infeasibility result or a global upper-bound improvement.
