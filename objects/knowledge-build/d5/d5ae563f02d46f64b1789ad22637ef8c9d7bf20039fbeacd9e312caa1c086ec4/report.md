# Knowledge-Formation Report

The existing root is updated to retain the global capacity question and governed benchmark interval while establishing one durable research program. The supplied batch contains no conflict records or reconciliation outcomes, so no active dispute node is required. Its unresolved matters are preserved as evidence gaps and open research questions rather than adjudicated.

All mathematical assessments below are attributed to primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`, concerning transaction `d638c346212db3e75f6a53dcebcfd09f55125852`.

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

the central unresolved question is the exact private-message sum-capacity

\[
C_{\mathrm{sum}}
=\sup\{R_1+R_2:(R_1,R_2)\text{ is achievable}\}.
\]

The governed current benchmark remains

\[
0.361642884421954615663441578150587\ldots
\le C_{\mathrm{sum}}\le
0.369316568803963.
\]

The supplied problem statement identifies the lower endpoint as the randomized-time-division value within Marton’s inner bound. It treats the reported decimal \(0.369296340638082\) as a numerical lead rather than a certified universal converse and does not pre-accept the separate fixed-pair artifact value \(0.369296945969202842443\).

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` concludes that the structural and finite-grid results assessed in this build improve neither endpoint. In particular:

- the exact three-point-grid value is a lower approximation to a fixed-receiver outer-bound functional, not a capacity upper bound;
- the midpoint localization result only excludes receiver pairs relative to a separately supplied threshold;
- no new achievable rate or smaller universal converse was established.

The exact value of \(C_{\mathrm{sum}}\) therefore remains open under the supplied judgments.

### Durable program structure

One research program is established directly beneath the root:

- `programs/auxiliary_receiver_outer_bound` — structural reduction, finite-grid analysis, exact three-point-grid results, certification status, and the unresolved continuum bridge for the Gohari–Liu–Nair auxiliary-receiver outer bound.

No conflict records or reconciliation outcomes were supplied. The source-transcription and continuum issues are active evidence gaps, not conflicts between opposed judgments.

### Provenance

- **Primary judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Judged transaction and evidence:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Global benchmark:** Supplied problem statement
- **Conflict status:** No supplied conflict records

## Change: root

The previous root stated that no research programs existed. This build retains the unchanged global capacity question and benchmark interval while adding the first durable program for the accepted structural and finite-grid auxiliary-receiver results. No numerical frontier change is recorded because the governing judgment expressly found none.

## Node: programs/auxiliary_receiver_outer_bound

- **Title:** Auxiliary-receiver outer-bound program
- **Type:** Program
- **Status:** Active
- **Parent:** `root`

### Program scope

This program studies the Gohari–Liu–Nair two-auxiliary-receiver outer-bound formulation through structural reductions of the receiver channels \(G,K\), finite-posterior-grid optimization, exact symbolic certificates, and possible bridges to the full continuum receiver functional.

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` supports, within their stated scopes:

1. reducing suitable finite \(T_{G,K|X,Y,Z}\) laws to conditionally independent input-only channels;
2. reducing each receiver to at most the grid size in a fixed finite-grid auxiliary optimization;
3. evaluating the encoded three-point-grid receiver infimum exactly;
4. obtaining a midpoint-information coercive lower bound for arbitrary receiver pairs.

The program does **not** currently provide:

- a continuum receiver-cardinality theorem;
- convergence of finite posterior grids to the full functional;
- interchange of the receiver infimum with a grid limit;
- reflected-pair sufficiency for the continuum optimization;
- a certified global minimization of the full functional \(B(G,K)\);
- an improved achievable sum rate or universal capacity converse.

Identification of the structural and exact symbolic results with every branch and side condition of the external manuscript remains conditional on the supplied term and row transcription. The hard-coded rows can be checked exactly after that transcription is accepted, but the absent manuscript equations prevent independent comparison within the supplied evidence.

### Current program nodes

- `programs/auxiliary_receiver_outer_bound/input_only_reduction`
- `programs/auxiliary_receiver_outer_bound/finite_grid_receiver_cardinality`
- `programs/auxiliary_receiver_outer_bound/three_point_grid_optimum`
- `programs/auxiliary_receiver_outer_bound/midpoint_coercivity`
- `programs/auxiliary_receiver_outer_bound/source_transcription_fidelity`
- `programs/auxiliary_receiver_outer_bound/certificate_reproducibility`
- `programs/auxiliary_receiver_outer_bound/continuum_bridge`

### Credit and provenance

The immutable judgment reports that the transaction attributes the three source artifacts and their port to Robert Raynor and disclaims new authorship arising merely from the port. That credit statement is carried forward without independent reassessment. The judgment also notes that the reported repository and historical acceptance provenance was not independently verifiable from the supplied files.

- **Primary judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`

## Change: programs/auxiliary_receiver_outer_bound

This new program preserves a coherent long-lived agenda centered on auxiliary-receiver outer bounds. It groups the accepted structural and finite-grid results with their certification limits and unresolved continuum dependency without treating the underlying transaction or artifacts as knowledge nodes.

## Node: programs/auxiliary_receiver_outer_bound/input_only_reduction

- **Title:** Input-only reduction for the auxiliary receivers
- **Type:** Structural result
- **Status:** Supported with qualification
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` supports the following reduction with high confidence for constraint systems having the audited single-output structure.

For any finite channel \(T_{G,K|X,Y,Z}\), let \(\bar T_{G|X}\) and \(\bar T_{K|X}\) be its induced single-receiver channels. Replacing it by

\[
T'_{G,K|X,Y,Z}(g,k|x,y,z)
=
\bar T_{G|X}(g|x)\bar T_{K|X}(k|x)
\]

preserves the joint laws needed to evaluate terms of the forms

\[
I(S;G|R)
\qquad\text{and}\qquad
I(S;K|R),
\]

where \(S\) and \(R\) are formed from \(X\) and the auxiliary variables. The \(Y\)- and \(Z\)-marginal terms are unchanged as well. Signed sums and minima made only from those preserved quantities therefore remain unchanged. Conversely, any input-only pair \(Q_{G|X},Q_{K|X}\) is already admissible in the original family by ignoring \(Y,Z\).

Under that syntactic condition, conditional correlation between \(G\) and \(K\), and output dependence beyond \(X\), are irrelevant to the attainable constraint set.

### Scope and uncertainty

The reduction does not cover formulations containing joint or output-conditioned terms such as

\[
I(S;G,K|R)
\quad\text{or}\quad
I(S;Y|G).
\]

Its application to every branch of the cited equations (19a)–(19p) and both side conditions remains conditional on the supplied term audit being faithful and exhaustive. The complete manuscript equations were not included in the evidence, so that external identification is not independently certified.

### Provenance

- **Supporting and qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Confidence recorded by judgment:** High, conditional on transcription fidelity

## Change: programs/auxiliary_receiver_outer_bound/input_only_reduction

This new node records the durable marginal-law reduction separately from the finite-grid results. It preserves the judgment’s high-confidence support while retaining the explicit dependence on an unverified audit of the external manuscript’s term structure.

## Node: programs/auxiliary_receiver_outer_bound/finite_grid_receiver_cardinality

- **Title:** Receiver cardinality on a finite posterior grid
- **Type:** Cardinality theorem
- **Status:** Supported with qualification
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Let \(Q\subset[0,1]\) be an \(N\)-point posterior grid containing

\[
0,\quad \frac12,\quad 1.
\]

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` supports with high confidence that, for the fair-input auxiliary optimization in which every auxiliary posterior is restricted to \(Q\), each finite-output binary-input receiver can be replaced by a receiver with at most \(N\) outputs without changing the restricted LP value.

The judgment records the following basis for the cardinality count:

- a finite-output receiver is represented by a posterior measure of mean \(1/2\);
- preserving the mean and the \(N-2\) nonendpoint information samples gives a vector in dimension \(N-1\);
- Carathéodory’s theorem therefore yields a representing measure with at most \(N\) atoms, rather than \(N+1\);
- preserving receiver information samples on \(Q\) preserves the relevant single-receiver mutual-information terms for auxiliary posteriors in \(Q\).

If \(Q\) is closed under \(q\mapsto1-q\), the reduction also preserves reflected receiver pairs through the relation between a receiver and its reflected posterior measure.

### Scope

This result is only a receiver-output cardinality theorem for a **fixed finite-grid auxiliary optimization**. It does not establish that:

- the replacement receiver’s posterior atoms lie on \(Q\);
- a comparable output-cardinality bound holds for the continuum problem;
- finite-grid values converge to the full receiver functional;
- a receiver infimum can be interchanged with a grid limit;
- reflected pairs suffice among arbitrary continuum receiver pairs.

Application to the named 30-row LP also depends on the asserted fact that every relevant row can be expressed using the audited single-receiver posterior samples.

### Provenance

- **Supporting and qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Confidence recorded by judgment:** High for the finite-grid theorem

## Change: programs/auxiliary_receiver_outer_bound/finite_grid_receiver_cardinality

This new node isolates the durable finite-grid receiver-cardinality theorem. Its scope is limited to fixed finite-grid optimization so that it is not misread as a continuum cardinality or convergence result.

## Node: programs/auxiliary_receiver_outer_bound/three_point_grid_optimum

- **Title:** Exact auxiliary-receiver optimum on the three-point posterior grid
- **Type:** Exact finite-grid result
- **Status:** Supported with documentation and transcription qualifications
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Define

\[
Q_0=\left\{0,\frac12,1\right\},
\qquad
c=h_2(1/4)-\frac12.
\]

For the supplied encoded 30-row formulation, primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` supports with high confidence that

\[
\inf_{G,K}V_{Q_0}(G,K)
=
\inf_m V_{Q_0}(m,m^\circ)
=
c.
\]

The first infimum ranges over finite-output receiver pairs, while the second is restricted to reflected pairs.

The judgment records two matching components:

- A \(W=X\) witness, with \(U,V\) constant in each auxiliary group, supports the universal lower bound
  \[
  V_{Q_0}(G,K)\ge c
  \]
  for every receiver pair in the encoded system.
- The reflection-invariant revealing-erasure posterior measure
  \[
  m_E=\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
  \]
  gives identical sampled curves for \(Y,G,K,Z\) on \(Q_0\). The supplied `SL(1,U)` row then yields
  \[
  R_1+R_2\le c,
  \]
  providing the matching upper construction in the reflected class.

### Certification and scope

The exact symbolic code checks the hard-coded row system, including the cancellation used for the matching upper row. The supplied checker described as a direct `W=X` audit is not actually that checker; consequently, the direct lower-witness argument is carried by the prose and row table, with additional support from the coercivity certificate.

The result’s identification with the external manuscript remains conditional on row-transcription fidelity.

This exact value is not a capacity converse. The judgment expressly records

\[
V_{Q_0}(G,K)\le B(G,K),
\]

because restricting auxiliary posteriors lowers the inner maximization. Thus the value \(c\) cannot replace the governed upper bound on \(C_{\mathrm{sum}}\).

### Provenance

- **Supporting and qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Confidence recorded by judgment:** High for the encoded 30-row formulation

## Change: programs/auxiliary_receiver_outer_bound/three_point_grid_optimum

This new node records the exact three-point-grid receiver optimization as a finite-grid result rather than a capacity bound. The node retains both the checker mismatch and the unverified manuscript-transcription dependency attached by the judgment.

## Node: programs/auxiliary_receiver_outer_bound/midpoint_coercivity

- **Title:** Midpoint-information coercive lower bound
- **Type:** Finite-grid lower-bound theorem
- **Status:** Supported with scope qualification
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Let

\[
g=I_G(1/2),\qquad k=I_K(1/2),
\qquad
c=h_2(1/4)-\frac12,
\]

and define

\[
F(x)=\frac{2c\max\{c,x\}}{c+x}.
\]

For the encoded 30-row \(Q_0\) problem, primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` supports with high confidence that

\[
B(G,K)\ge V_0(g,k)\ge \max\{F(g),F(k)\}.
\]

The judgment attributes this lower bound to the supplied H, L, and X witness families and their exact rational-polynomial row audit. It records that the three witness regimes cover high, low, and crossing configurations of the two midpoint informations. The symbolic checker:

- rebuilds the 30 labeled rows from hard-coded path formulas;
- verifies the witness block constraints;
- computes exact rational-polynomial slacks;
- verifies their coefficientwise nonnegativity after the stated substitutions;
- uses no floating-point optimizer.

The passage from the restricted \(Q_0\) witnesses to the full fixed-receiver functional has the supported direction

\[
B(G,K)\ge V(1/2;G,K)\ge V_0(g,k).
\]

For any \(U\) satisfying

\[
c\le U<2c,
\]

the judgment also supports the necessary implication

\[
B(G,K)\le U
\quad\Longrightarrow\quad
\frac{2c^2}{U}-c
\le g,k\le
\frac{Uc}{2c-U}.
\]

### Scope

The midpoint interval is a necessary localization condition. It is not:

- a sufficient condition for \(B(G,K)\le U\);
- a global minimization of \(B(G,K)\);
- a proof of reflected optimality;
- a capacity converse.

The exact symbolic certification begins after accepting the hard-coded rows as the intended manuscript constraint system. External row fidelity remains unverified.

### Provenance

- **Supporting and qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Confidence recorded by judgment:** High for the encoded \(Q_0\) row system

## Change: programs/auxiliary_receiver_outer_bound/midpoint_coercivity

This new node preserves the coercive midpoint theorem and its inversion as a distinct localization tool. It explicitly prevents the necessary condition from being promoted to reflected optimality, global minimization, or a capacity bound.

## Node: programs/auxiliary_receiver_outer_bound/source_transcription_fidelity

- **Title:** Fidelity of the external Theorem 9 transcription
- **Type:** Active evidence gap
- **Status:** Unresolved
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

The complete external equations (19a)–(19p) and an independently checkable copy of the cited manuscript formulation were not included in the judged evidence.

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` therefore does not decide whether:

- the supplied single-output term audit exhausts every manuscript branch and side condition;
- all 30 hard-coded rows exactly reproduce the manuscript;
- every side-condition orientation is correct;
- every row coefficient was transcribed correctly.

The marginal-law and finite-grid arguments are independently supported for systems possessing the stated structure. The exact symbolic code certifies the hard-coded rows after those rows are accepted. What remains uncertain is the identification of that encoded system with the complete external source.

No opposing primary judgments or reconciliation outcomes were supplied. This node is therefore an unresolved evidence dependency, not an adjudicated dispute.

### Provenance

- **Uncertainty judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Conflict status:** No supplied conflict record or reconciliation

## Change: programs/auxiliary_receiver_outer_bound/source_transcription_fidelity

This new node preserves the judgment’s unresolved source-comparison issue as a durable validation dependency. It prevents exact checks of the encoded rows from being silently treated as certification of the absent manuscript equations.

## Node: programs/auxiliary_receiver_outer_bound/certificate_reproducibility

- **Title:** Reproducibility status of the three-point-grid certificates
- **Type:** Certification finding
- **Status:** Confirmed documentation defect with mathematical scope preserved
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` refutes the documentation claim that the supplied `frontier-global-bridge` checker directly audits the \(W=X\) witness table and prints the described \(W=X\) messages.

The judgment finds that this checker is instead byte-for-byte the coercivity checker supplied under `frontier-q0-coercive`. Consequently:

- the two documented reproduction commands execute duplicate mathematical content;
- they are not independent corroborations;
- the `frontier-global-bridge` reproduction description is inaccurate;
- the supplied executable does not perform the specifically described direct \(W=X\) audit.

The judgment does not treat this defect as invalidating the finite-grid mathematical conclusions. The included checker verifies the stronger coercive lower bound and the matching upper row for the hard-coded system, while the prose proof and row table carry the direct \(W=X\) argument.

The executable certification remains subject to the separate source-transcription uncertainty: it checks the encoded rows, not their fidelity to the absent external manuscript equations.

### Provenance

- **Refuting and qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`

## Change: programs/auxiliary_receiver_outer_bound/certificate_reproducibility

This new node records the confirmed checker/documentation mismatch without turning it into a mathematical refutation. It also prevents the duplicated checker commands from being counted as independent evidence.

## Node: programs/auxiliary_receiver_outer_bound/continuum_bridge

- **Title:** Bridge from finite posterior grids to the full receiver functional
- **Type:** Open research question
- **Status:** Active and unresolved
- **Parent:** `programs/auxiliary_receiver_outer_bound`

### Current knowledge

Primary judgment `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99` concludes that the accepted structural and finite-grid results do not establish a bridge to a certified global optimization of the full receiver functional \(B(G,K)\).

In particular, the supplied evidence contains no proof of:

1. a receiver-output cardinality bound for the continuum problem;
2. convergence of finite posterior-grid optimizations to the full functional;
3. interchange of the receiver infimum with a posterior-grid limit;
4. sufficiency or optimality of reflected receiver pairs in the full optimization;
5. a certified global minimization of \(B(G,K)\).

The exact three-point-grid value and midpoint coercive bound remain lower approximations or necessary localization tools for fixed receiver pairs. They do not by themselves yield a universal converse on \(C_{\mathrm{sum}}\).

According to the judgment, these missing continuum ingredients remain decisive obstacles to turning the finite-grid foundations into an improved capacity upper bound. No reconciliation or later supplied judgment resolves them.

### Provenance

- **Qualifying judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Subject and evidence transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Conflict status:** No supplied conflict record or reconciliation; the question remains open for lack of evidence

## Change: programs/auxiliary_receiver_outer_bound/continuum_bridge

This new node preserves the missing continuum step as an explicit research dependency. It separates valid finite-grid progress from the unproved limit, symmetry, and global-minimization statements needed for a new capacity converse.
