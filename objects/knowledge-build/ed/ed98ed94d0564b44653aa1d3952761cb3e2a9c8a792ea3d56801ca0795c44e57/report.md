# Knowledge-formation report

## Node: root

- **Title:** Research state for BSSC private-message sum-capacity
- **Type:** Root
- **Status:** Active
- **Parent:** None

### Current knowledge

For the binary-input broadcast channel with marginals

\[
P_{Y|X}=
\begin{pmatrix}
\tfrac12&\tfrac12\\
0&1
\end{pmatrix},
\qquad
P_{Z|X}=
\begin{pmatrix}
1&0\\
\tfrac12&\tfrac12
\end{pmatrix},
\]

the central unresolved question remains the exact private-message sum-capacity

\[
C_{\mathrm{sum}}
=\sup\{R_1+R_2:(R_1,R_2)\text{ is achievable}\}.
\]

The governed current benchmark is

\[
\boxed{
0.361642884421954615663441578150587\ldots
\le C_{\mathrm{sum}}
\le 0.369296945969202842443
}.
\]

The lower endpoint remains the randomized-time-division value within Marton’s inner bound, as identified in the supplied problem statement. No supplied judgment establishes a larger achievable rate.

Primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` supports the improved universal upper bound

\[
C_{\mathrm{sum}}\le 0.369296945969202842443.
\]

According to that judgment, the converse is obtained from the full Gohari–Liu–Nair Theorem 9 outer bound at one specified reflected binary auxiliary-receiver pair. It is backed by an exact nonnegative six-row dual combination, continuum-wide outward-rounded interval majorants over the complete posterior interval \([0,1]\), and analytic maximization over every input prior. It is not a finite posterior-grid certificate.

The exact value of \(C_{\mathrm{sum}}\) remains unknown. In particular, the accepted fixed-pair converse does not establish:

- matching achievability;
- global optimality of the selected auxiliary-receiver pair;
- global sufficiency of binary or reflected auxiliary receivers;
- global optimality of the selected six-row dual face; or
- certification of the smaller numerical lead
  \[
  0.369296340638082.
  \]

The earlier exact three-point-grid result remains a lower approximation to a fixed-receiver outer-bound functional rather than a capacity upper bound. Midpoint localization remains a necessary localization result relative to a supplied threshold. Neither result is displaced by the continuous fixed-pair certificate, but neither determines the global auxiliary optimization.

### Durable program structure

The established program directly beneath the root is:

- `programs/auxiliary_receiver_outer_bound` — structural reductions, finite-grid analysis, continuous fixed-pair converses, exact dual-functional identities, certificate reproducibility, and the unresolved global auxiliary-receiver optimization associated with the Gohari–Liu–Nair outer bound.

No conflict records or reconciliation outcomes were supplied. The remaining uncertainties are open mathematical or evidentiary dependencies, not conflicts between opposed primary judgments.

### Provenance

- **Earlier primary judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Current frontier judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Earlier subject transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Frontier subject transaction:** `7e7626cbff7270572d51a8fda719154ab602907f`
- **Lower-bound source:** Supplied problem statement
- **Conflict status:** No supplied conflict or reconciliation records

## Change: root

The frontier judgment accepts a certified universal converse below the former governed upper endpoint \(0.369316568803963\). The root therefore records \(0.369296945969202842443\) as the current upper bound while preserving the unchanged lower bound, the open exact-capacity question, and the uncertified status of the smaller numerical lead.

## Node: programs/auxiliary_receiver_outer_bound

- **Title:** Auxiliary-receiver outer-bound program
- **Type:** Program
- **Status:** Active
- **Parent:** `root`

### Program scope

This program studies the Gohari–Liu–Nair two-auxiliary-receiver outer bound through structural reductions of the receiver channels \(G,K\), finite-posterior-grid optimization, exact symbolic dual certificates, continuous posterior majorants, symmetry identities, and the unresolved optimization over all admissible auxiliary-receiver pairs and dual choices.

### Established results

The supplied primary judgments support the following results within their stated scopes:

1. **Input-only reduction.** Suitable finite laws \(T_{G,K|X,Y,Z}\) can be reduced to conditionally independent input-only receiver channels under the conditions assessed by the earlier judgment.

2. **Finite-grid receiver cardinality.** For a fixed finite posterior grid, each auxiliary receiver can be reduced to at most the grid size in the corresponding finite-grid optimization.

3. **Exact three-point-grid evaluation.** The encoded three-point-grid receiver infimum has an exact symbolic evaluation. This is a finite-grid lower approximation to a receiver functional, not a universal capacity upper bound.

4. **Midpoint coercivity.** A midpoint-information lower bound supplies a necessary localization tool for auxiliary-receiver pairs relative to a separately supplied threshold.

5. **Continuous fixed-pair converse.** For the specified reflected binary pair
   \[
   G=(0.206961624915382,0.826953249115544),
   \qquad
   K=(0.173046750884456,0.793038375084618),
   \]
   the full Theorem 9 outer bound gives
   \[
   C_{\mathrm{sum}}\le0.369296945969202842443.
   \]
   The accepted certificate covers the complete posterior continuum and analytically maximizes over all input priors.

6. **Exact skew-invariant representation.** For \(0\le\epsilon\le1/3\), the particular frontier six-row functional has an exactly equal nonnegative skew-invariant six-row representation for every input prior, every auxiliary-receiver pair, and every admissible three-group hierarchy. This is an identity for that functional, not a theorem that invariant duals are globally sufficient.

7. **Narrow rounded-majorant repair.** For one earlier frozen group-\(b\) slope and contact construction, the zero-intercept affine line is infeasible; an intercept of \(10^{-33}\) repairs the directed gap. This does not rule out every possible zero-intercept supporting line.

### Remaining limitations

The program does not currently establish:

- a continuum receiver-output cardinality theorem;
- convergence of finite posterior-grid receiver optimizations to the full receiver functional;
- interchange of the receiver infimum with a posterior-grid limit;
- global sufficiency of binary auxiliary receivers;
- global sufficiency of reflected receiver pairs;
- global sufficiency of skew-invariant duals;
- optimality of the certified receiver pair or its chosen value of \(\epsilon\);
- a certified global minimum over all \(G,K\) and all admissible Theorem 9 dual choices;
- certification or refutation of the numerical lead \(0.369296340638082\);
- a matching achievable rate; or
- the exact private-message sum-capacity.

The fixed-pair result is nevertheless a valid universal converse according to the frontier judgment. Its validity does not depend on proving that the selected pair is globally optimal.

### Source and formalization boundary

The internal exact row expansion, rate normalization, posterior-functional identity, and continuous interval strategy are supported by the judgments. External trust remains in:

- the validity of the cited Theorem 9;
- correct transcription of the six selected manuscript rows and the side-condition orientation;
- the documented behavior of Python’s `Decimal.ln` used by the interval implementation; and
- the previously established quotient convention when the invariant functional is identified with named rank-eight coordinates.

The complete manuscript row comparison and a proof-assistant formalization were not supplied.

### Current program nodes

- `programs/auxiliary_receiver_outer_bound/input_only_reduction`
- `programs/auxiliary_receiver_outer_bound/finite_grid_receiver_cardinality`
- `programs/auxiliary_receiver_outer_bound/three_point_grid_optimum`
- `programs/auxiliary_receiver_outer_bound/midpoint_coercivity`
- `programs/auxiliary_receiver_outer_bound/fixed_pair_continuous_converse`
- `programs/auxiliary_receiver_outer_bound/skew_invariant_six_row_functional`
- `programs/auxiliary_receiver_outer_bound/source_transcription_fidelity`
- `programs/auxiliary_receiver_outer_bound/certificate_reproducibility`
- `programs/auxiliary_receiver_outer_bound/continuum_bridge`

### Credit and provenance

The immutable judgments carry forward the following attribution without independent reassessment:

- the first continuous certificate, improved frontier certificate, and invariant-functional artifact are attributed to **Robert Raynor**;
- the microscopic-backoff repair is attributed to **Red Team D**, committed by Robert Raynor;
- the transactions are attributed ports and do not claim new mathematical authorship merely from porting.

Provenance:

- `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- `d638c346212db3e75f6a53dcebcfd09f55125852`
- `7e7626cbff7270572d51a8fda719154ab602907f`

## Change: programs/auxiliary_receiver_outer_bound

The program previously recorded no improved universal converse. The frontier judgment now supports a continuous full-Theorem-9 fixed-pair upper bound and an exact invariant representation of its six-row functional, requiring the program’s holdings, limitations, child inventory, and source boundaries to be revised without changing the established program identity.

## Node: programs/auxiliary_receiver_outer_bound/fixed_pair_continuous_converse

- **Title:** Continuous full-Theorem-9 converse for a fixed reflected binary receiver pair
- **Type:** Result
- **Status:** Established within stated trust boundaries
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` supports a continuous universal converse obtained from the full Gohari–Liu–Nair Theorem 9 outer bound at the exact binary auxiliary-receiver pair

\[
G=(0.206961624915382,0.826953249115544),
\]

\[
K=(0.173046750884456,0.793038375084618),
\]

where each ordered pair gives \(P(A=0|X=0),P(A=0|X=1)\), and \(K\) is the input/output reflection of \(G\).

The certified value satisfies

\[
\begin{aligned}
U\in[&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,\\
&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
\end{aligned}
\]

Consequently,

\[
\boxed{C_{\mathrm{sum}}\le0.369296945969202842443}.
\]

### Certified proof components

The judgment accepts the following components as supporting the converse:

1. With
   \[
   \epsilon=0.000173428163029,
   \]
   five rate inequalities and one nonnegative side-condition expression are combined with weights
   \[
   \epsilon,\ \epsilon,\ \epsilon,\ 
   \frac{1-\epsilon}{2},\
   \frac{1-3\epsilon}{2},\
   \epsilon.
   \]
   Exact rational arithmetic verifies nonnegativity and coefficient one on each of \(R_1\) and \(R_2\).

2. Standard binary-posterior mutual-information identities rewrite the selected right side in terms of posterior variables. Dropping compatibility conditions beyond the required martingale constraints enlarges the optimization class in the direction permitted for a converse.

3. An exact sparse posterior-tensor audit verifies the claimed three-group functional and the root-level cancellation
   \[
   c_Y=c_Z=\frac{1+\epsilon}{2},
   \qquad
   c_G=c_K=0.
   \]

4. Affine majorants are certified over the entire posterior interval \([0,1]\). The judgment reports exact curvature-sign reductions, analytic control of concave and convex regions, directed interval checks at required contact and endpoint quantities, and adaptive fail-closed interval subdivision elsewhere.

5. After cancellation of the auxiliary-receiver root coefficients and total affine slope, the remaining prior-dependent term is
   \[
   \frac{1+\epsilon}{2}\bigl(I_Y(q_0)+I_Z(q_0)\bigr)+\text{constant}.
   \]
   The judgment supports analytic maximization at \(q_0=1/2\) using concavity and the reflection relation \(I_Z(q)=I_Y(1-q)\).

6. The final numerical enclosure uses outward-rounded high-precision decimal intervals. The upper endpoint lies below the displayed rounded bound.

### Scope and limitations

This result is a universal capacity upper bound at one permitted fixed auxiliary-receiver pair. It does not establish:

- optimality of that pair;
- binary- or reflected-pair sufficiency for the global receiver optimization;
- global optimality of the selected six-row dual;
- equality between the Theorem 9 outer bound and capacity;
- validity of the smaller numerical lead \(0.369296340638082\); or
- any matching achievable sum rate.

The judgment assigns high confidence conditional on the cited Theorem 9, correct transcription of the six selected rows and side-condition orientation, and the documented logarithm behavior used by the interval implementation.

### Credit and provenance

The improved frontier certificate is attributed by the immutable judgment to **Robert Raynor**. The act of porting it is not credited as new mathematical authorship.

- **Primary judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Subject and evidence transaction:** `7e7626cbff7270572d51a8fda719154ab602907f`
- **Conflict status:** No supplied conflict or reconciliation record

## Change: programs/auxiliary_receiver_outer_bound/fixed_pair_continuous_converse

This durable result node is created because the frontier judgment accepts a continuum-wide fixed-pair Theorem 9 certificate that improves the governed capacity upper bound. It is separated from finite-grid results and from the unresolved global receiver optimization because its mathematical content and scope remain meaningful independently of the transaction that supplied it.

## Node: programs/auxiliary_receiver_outer_bound/skew_invariant_six_row_functional

- **Title:** Exact skew-invariant representation of the frontier six-row functional
- **Type:** Structural result
- **Status:** Established, with a quotient-coordinate qualification
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` supports the following functional identity.

For every

\[
0\le\epsilon\le\frac13,
\]

the non-invariant six-row combination used by the frontier certificate induces exactly the same posterior-hierarchy functional as a nonnegative six-row combination whose weights are invariant under the BSSC skew involution.

The identity holds for:

- every input prior;
- every auxiliary-receiver pair \(G,K\); and
- every admissible three-group hierarchy.

It is not restricted to the particular reflected pair used by the continuous numerical certificate.

The exact audit supports that:

- both row combinations have rate vector \((1,1)\);
- their \(W,U,V\) tensor coefficients agree group by group;
- their only root-level residuals occur in the \(G,K\) columns;
- those residuals sum to zero across the three groups for each receiver column; and
- all invariant weights are nonnegative throughout \(0\le\epsilon\le1/3\).

The equality is therefore an identity of the weighted hierarchy functionals before posterior-envelope optimization or maximization over the input prior.

### Scope limitations

The result establishes that this particular frontier functional has a representative inside the skew-invariant dual cone. It does not establish:

- that every optimal Theorem 9 dual has an invariant representative;
- that optimization may globally be restricted to invariant duals;
- that auxiliary-receiver pairs may be restricted to reflected pairs;
- that the certified pair or value of \(\epsilon\) is optimal; or
- that leaving the invariant cone cannot improve the global converse.

### Rank-eight quotient coordinates

The encoded invariant functional is algebraically consistent with the asserted quotient point

\[
\left(
\frac{1-\epsilon}{2},
0,
\epsilon,
0,
0,
0,
0,
\frac{1-\epsilon}{2}
\right)
\]

and normalization

\[
2s_B+s_C+s_D+s_E=1.
\]

The judgment does not independently reproduce the full rank-eight quotient theorem or derive the named coordinate map from all 15 skew-paired rows. Identification with the particular named coordinates

\[
(s_B,s_C,s_D,s_E,s_{N_0},s_{N_1},s_{F_0},s_{F_1})
\]

therefore remains conditional on the previously established quotient convention. This qualification does not affect the exact functional identity or the capacity upper bound.

### Credit and provenance

The invariant-functional artifact is attributed by the immutable judgment to **Robert Raynor**.

- **Primary judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Subject and evidence transaction:** `7e7626cbff7270572d51a8fda719154ab602907f`
- **Conflict status:** No supplied conflict or reconciliation record

## Change: programs/auxiliary_receiver_outer_bound/skew_invariant_six_row_functional

This node is created because the accepted exact identity is a durable structural result with broader scope than the certified numerical receiver pair. The quotient-coordinate qualification is retained explicitly so that algebraic consistency is not silently promoted into an independently reproduced rank-eight quotient theorem.

## Node: programs/auxiliary_receiver_outer_bound/continuum_bridge

- **Title:** Bridge from local or finite auxiliary-receiver analyses to the global receiver functional
- **Type:** Open research question
- **Status:** Active and unresolved
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

A continuum certificate is now established for one specified reflected binary auxiliary-receiver pair. Primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` supports that this fixed-pair full-Theorem-9 calculation yields the universal converse

\[
C_{\mathrm{sum}}\le0.369296945969202842443.
\]

Thus the absence of a finite-grid-to-continuum theorem does not prevent that particular fixed-pair converse: its posterior majorants directly cover all of \([0,1]\), and its maximization over the input prior is analytic.

The larger global bridge remains unresolved. The supplied judgments do not establish:

1. a continuum receiver-output cardinality theorem for the global optimization;
2. convergence of finite posterior-grid receiver optimizations to the full receiver functional;
3. interchange of the receiver infimum with a posterior-grid limit;
4. global sufficiency of binary auxiliary receivers;
5. global sufficiency or optimality of reflected receiver pairs;
6. global sufficiency of skew-invariant duals;
7. optimality of the certified pair, the selected \(\epsilon\), or the selected dual face;
8. a certified global minimization over all admissible \(G,K\) and dual choices;
9. certification or refutation of the numerical lead \(0.369296340638082\); or
10. matching achievability at the certified upper endpoint.

The exact three-point-grid result remains a finite-grid lower approximation to a receiver functional. Midpoint coercivity remains a necessary localization tool. The continuous fixed-pair certificate is stronger in a different direction: it supplies a valid universal converse without resolving the global auxiliary-receiver optimization.

No supplied judgment determines the exact private-message sum-capacity.

### Provenance

- **Earlier qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Frontier qualifying judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Evidence transactions:** `d638c346212db3e75f6a53dcebcfd09f55125852`, `7e7626cbff7270572d51a8fda719154ab602907f`
- **Conflict status:** No supplied conflict or reconciliation; the global question remains open for lack of a resolving result

## Change: programs/auxiliary_receiver_outer_bound/continuum_bridge

The earlier formulation treated a certified continuum converse as wholly absent. The frontier judgment now establishes such a converse for one fixed pair, so the open question is narrowed to global receiver-pair, cardinality, symmetry, dual-optimality, and matching-achievability issues rather than continuum coverage of that fixed pair.

## Node: programs/auxiliary_receiver_outer_bound/source_transcription_fidelity

- **Title:** Fidelity of the Theorem 9 transcription and quotient-coordinate identification
- **Type:** Active evidence dependency
- **Status:** Partially supported and partially unresolved
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

The supplied judgments distinguish internally audited algebra from comparison against the complete external Gohari–Liu–Nair manuscript.

For the fixed-pair converse, primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` supports the internal exact audit of:

- the six selected row weights;
- nonnegativity of those weights;
- exact normalization to rate coefficients \((1,1)\);
- the sparse posterior-tensor expansion;
- the claimed three-group closed form;
- the root-level coefficient cancellation; and
- the exact equality between the original and skew-invariant six-row functionals.

The judgment accepts the resulting full-Theorem-9 fixed-pair converse with high confidence, conditional on:

1. validity of the cited Theorem 9;
2. correct transcription of the six selected manuscript rows;
3. correct orientation of the selected side condition; and
4. the documented logarithm behavior used by the interval implementation.

The complete external equations and a row-by-row comparison against all manuscript branches were not supplied. It therefore remains an external trust point whether the selected rows and side-condition signs exactly reproduce the source manuscript.

For the invariant representation, the encoded map to the claimed rank-eight quotient coordinates is algebraically consistent. The supplied evidence does not independently reproduce the full quotient theorem or derive the named map from all 15 skew-paired rows. The functional identity is supported independently of that coordinate naming, while the coordinate identification remains conditional on the prior quotient convention.

The earlier finite-grid symbolic code likewise certifies its hard-coded rows after accepting their transcription. Uncertainty about full source comparison does not overturn the internally supported algebraic statements for the encoded systems.

No opposing primary judgment or reconciliation outcome was supplied. These are evidentiary qualifications rather than an active adjudicatory conflict.

### Provenance

- **Earlier uncertainty judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Frontier judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Evidence transactions:** `d638c346212db3e75f6a53dcebcfd09f55125852`, `7e7626cbff7270572d51a8fda719154ab602907f`
- **Conflict status:** No supplied conflict or reconciliation record

## Change: programs/auxiliary_receiver_outer_bound/source_transcription_fidelity

The frontier judgment supports the internal six-row and invariant-functional audits while retaining external trust in manuscript transcription and qualifying the rank-eight coordinate naming. This node is refined to distinguish accepted encoded algebra from the still-unreproduced complete source and quotient-theorem comparisons.

## Node: programs/auxiliary_receiver_outer_bound/certificate_reproducibility

- **Title:** Reproducibility and directed-certification status
- **Type:** Method and evidence-status node
- **Status:** Active
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

The supplied judgments support two distinct forms of auditable certification within this program.

#### Exact encoded algebra

Exact rational arithmetic is used to audit:

- nonnegative row weights;
- exact rate normalization;
- sparse posterior-tensor expansions;
- equality with the claimed three-group functional;
- root-level cancellations;
- equality of the original and skew-invariant six-row functionals; and
- the encoded finite-grid rows, conditional on accepting their source transcription.

These checks reduce the risk that numerical optimization is being applied to a different encoded functional than the one stated.

#### Continuous fixed-pair certificate

For the accepted frontier converse, the judgment reports a fail-closed continuous verification over all posterior values in \([0,1]\), rather than a finite grid. Its supported reproducibility features include:

- exact curvature-sign calculations where used;
- analytic treatment of concave and convex regions;
- directed interval enclosures for required endpoint and contact inequalities;
- adaptive interval subdivision on the remaining regions;
- explicit failure on an uncertified cell or exceeded resource budget;
- 136 accepted regular cells in the reported final check;
- analytic, rather than sampled, maximization over the input prior; and
- outward-rounded 80-digit decimal intervals for the final entropy and logarithm evaluations.

The hostile-context reruns reported by the judgment are useful implementation checks but are not independently treated as proof of interval soundness. The interval layer retains a trust dependency on Python’s documented `Decimal.ln` behavior. The certificate is not a proof-assistant formalization.

#### Rounded group-\(b\) majorant repair

For an earlier fixed pair and the exact frozen slope

\[
0.0026976853408719163997223206507487,
\]

the directed gap of the corresponding zero-intercept group-\(b\) line at the frozen contact point has a strictly negative upper endpoint, approximately

\[
-4.8921763736983316\ldots\times10^{-35}.
\]

Primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` therefore supports that this particular rounded zero-intercept line is infeasible. Adding an intercept of \(10^{-33}\) repairs the directed gap for that specified construction, including the stated local derivative allowance, with the remaining interval covered by adaptive subdivision.

This conclusion is narrow. It does not establish that every possible zero-intercept supporting line for the relevant curve is infeasible.

The several close fixed-pair endpoints appearing in the artifacts are not treated as conflicts: the certificates use different backoffs or different exact auxiliary-receiver pairs. The accepted frontier certificate provides the strongest governed endpoint among them.

### Provenance and credit

The first continuous certificate and improved frontier certificate are attributed to **Robert Raynor**. The microscopic-backoff repair is attributed to **Red Team D**, committed by Robert Raynor. Porting does not create a new mathematical authorship claim.

- **Earlier judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Frontier judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Evidence transactions:** `d638c346212db3e75f6a53dcebcfd09f55125852`, `7e7626cbff7270572d51a8fda719154ab602907f`
- **Conflict status:** No supplied conflict or reconciliation record

## Change: programs/auxiliary_receiver_outer_bound/certificate_reproducibility

The accepted frontier judgment adds a continuum-wide directed certificate, exact six-row audits, and a narrowly scoped repair of an earlier rounded majorant. These belong in the established reproducibility concept rather than in event-shaped nodes, with implementation trust boundaries and the limited scope of the repair recorded explicitly.
