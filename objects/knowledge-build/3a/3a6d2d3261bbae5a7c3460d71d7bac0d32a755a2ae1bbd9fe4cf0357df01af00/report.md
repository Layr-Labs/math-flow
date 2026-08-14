# Knowledge-Formation Report

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

the exact private-message sum-capacity

\[
C_{\mathrm{sum}}
=\sup\{R_1+R_2:(R_1,R_2)\text{ is achievable}\}
\]

remains unknown.

The governed current benchmark is unchanged:

\[
\boxed{
0.361642884421954615663441578150587\ldots
\le C_{\mathrm{sum}}
\le 0.369296945969202842443
}.
\]

The lower endpoint remains the randomized-time-division value within Marton’s inner bound, as identified by the supplied problem statement. No supplied judgment establishes a larger achievable rate.

Primary judgment `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44` supports the universal upper bound

\[
C_{\mathrm{sum}}\le 0.369296945969202842443.
\]

According to that judgment, the bound is obtained from the full Gohari–Liu–Nair Theorem 9 outer bound at a specified reflected binary auxiliary-receiver pair. Its fixed-pair certificate uses an exact nonnegative six-row dual combination, outward-rounded interval majorants over the full posterior interval \([0,1]\), and analytic maximization over every input prior. It is not merely a finite posterior-grid calculation.

The fixed-pair certificate does not establish:

- matching achievability;
- global optimality of the selected auxiliary-receiver pair;
- global sufficiency of binary or reflected auxiliary receivers;
- global optimality of the selected six-row dual face; or
- certification of the smaller numerical lead
  \[
  0.369296340638082.
  \]

The earlier exact three-point-grid result remains a lower approximation to a fixed-receiver outer-bound functional rather than a capacity upper bound. The earlier midpoint-localization result remains a necessary localization statement relative to its supplied threshold. Neither determines the global auxiliary-receiver optimization.

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` accepts, within its stated scope, a separate structural program concerning:

- an exact finite-block dependence-balance telescope;
- selected-coordinate fixed-map factorization and four rate inequalities;
- a sharp scalar BSSC posterior-support inequality;
- an actual finite entropic counterfeit for a specified coarse entropy relaxation; and
- a no-go result for strengthening that relaxation through universally valid finite-variable information inequalities or finitely many standard copy-lemma extensions.

Those results do not determine \(C_{\mathrm{sum}}\) or improve either endpoint of the governed interval.

Primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` additionally accepts a distinct program concerning two separately relaxed UV sum-rate scalar functionals. It supports:

- exact product additivity of the averaged scalar for arbitrary finite-alphabet broadcast channels, including correlated product-channel inputs and joint envelope auxiliaries;
- equality of the branchwise and averaged scalars for receiver-skew-symmetric channels;
- exact product additivity of the branchwise scalar for finite products of receiver-skew-symmetric channels; and
- the half-skew BSSC evaluation
  \[
  B_{\mathrm{br}}(P)=B_{\mathrm{avg}}(P)
  =2h_2(1/4)-\frac54
  =0.3725562489182657\ldots,
  \]
  together with the corresponding exact linear value at every finite product blocklength.

Under the UV derivation, this number is a valid but noncompetitive sum-rate upper bound:

\[
C_{\mathrm{sum}}
\le 2h_2(1/4)-\frac54.
\]

It is weaker than both the published benchmark upper endpoint \(0.369316568803963\) and the governed fixed-pair upper bound \(0.369296945969202842443\). It therefore changes neither side of the current capacity frontier and supplies no achievable-rate evidence.

The same decimal consequently has two distinct, separately governed meanings:

1. In the specified coarse entropy relaxation, it is an attained objective value whose witness alone supplies neither a lower nor an upper bound on BSSC capacity.
2. In the separately relaxed UV program, it is independently derived as a valid but weaker capacity upper bound.

These interpretations are compatible and must not be conflated.

### Durable program structure

The durable programs directly beneath the root are:

- `programs/auxiliary_receiver_outer_bound` — structural reductions, finite-grid analysis, continuous fixed-pair converses, exact dual-functional identities, certificate reproducibility, and unresolved global auxiliary-receiver optimization associated with the Gohari–Liu–Nair outer bound.
- `programs/dependence_balance_entropy_relaxation` — finite-block dependence-balance and selected-coordinate structure, together with BSSC-specific analysis of the capabilities and limitations of a specified coarse entropy relaxation.
- `programs/uv_relaxed_scalar` — averaged and branchwise separately relaxed UV scalar functionals, their tensorization properties, receiver-skew-symmetry reduction, and exact half-skew BSSC evaluation.

No conflict or reconciliation records were supplied. The remaining limitations are open mathematical or evidentiary dependencies rather than disputes between opposed primary judgments.

### Provenance

- **Lower-bound source:** Supplied problem statement
- **Earlier subject transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Earlier primary judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Fixed-pair subject transaction:** `7e7626cbff7270572d51a8fda719154ab602907f`
- **Fixed-pair primary judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Dependence-balance subject transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Dependence-balance primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **UV-scalar subject transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **UV-scalar primary judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Conflict status:** No supplied conflict or reconciliation records

## Change: root

The new primary judgment accepts a distinct UV-scalar research agenda and a valid but non-improving upper bound with the same numerical value as the existing coarse-relaxation objective. The root is revised to add that durable program, distinguish the two meanings of the shared decimal, and record that the governed capacity interval and exact-value status remain unchanged.

## Node: programs/dependence_balance_entropy_relaxation

- **Title:** Finite-block dependence balance and limits of coarse entropy relaxation
- **Type:** Program
- **Status:** Active
- **Parent:** `root`

### Current knowledge

This program collects two related agendas accepted by primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`:

1. extracting exact finite-block and selected-coordinate constraints from reliable private-message broadcast codes; and
2. determining what a specified coarse BSSC entropy relaxation can and cannot prove.

For the first agenda, the judgment accepts with high confidence:

- an exact dependence-balance telescope for every deterministic finite-block private-message code;
- a Fano-controlled normalized defect that vanishes along reliable bounded-rate code sequences;
- selected-coordinate factorization retaining the stronger property
  \[
  X=f_T(U,V),
  \]
  independent of the selected state \(W\); and
- two individual-rate and two sum-rate inequalities compatible with that factorization.

These conclusions remain sequence-level. The judgment finds that no simultaneous cardinality or compactness reduction has been established. Optimization over arbitrarily chosen small auxiliary alphabets would therefore not, by itself, certify a universal converse.

For the second agenda, the judgment accepts with high confidence:

- a global affine support for the fair-input BSSC posterior-information difference, sharp in its stated scalar direction;
- an actual finite joint distribution satisfying the specified structural, entropy, disjoint-subtuple BEC, and support constraints of the coarse relaxation;
- the relaxation objective value
  \[
  2h_2(1/4)-\frac54
  =0.3725562489182657\ldots;
  \]
- exact component accounting corroborated by a formal-entropy checker; and
- the conclusion that universal finite-variable information inequalities and any finite sequence of standard copy-lemma extensions cannot exclude this witness or force this particular relaxation below that value.

The no-go conclusion is restricted to the specified relaxation and the named universal-inequality and copy-lemma strengthening methods. It does not establish a limitation for every possible entropy formulation or converse method.

Within this program, attaining

\[
2h_2(1/4)-\frac54
\]

does not itself provide either an achievable rate or a capacity upper bound. The coarse relaxation is deliberately too weak for that interpretation. Primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` separately accepts the same numerical value as a valid upper bound derived from a different, separately relaxed UV functional. That independent UV interpretation does not convert the coarse entropy witness into a converse certificate.

This program currently provides no improvement to the governed BSSC sum-capacity interval and establishes no fixed-alphabet compactness theorem.

### Program nodes

- `programs/dependence_balance_entropy_relaxation/finite_block_telescope`
- `programs/dependence_balance_entropy_relaxation/selected_coordinate_constraints`
- `programs/dependence_balance_entropy_relaxation/uniform_bssc_posterior_support`
- `programs/dependence_balance_entropy_relaxation/coarse_entropy_counterfeit`
- `programs/dependence_balance_entropy_relaxation/universal_inequality_copy_no_go`

### Provenance

- **Principal subject transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Principal primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Interpretive context transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **Interpretive context judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation

The program’s accepted structural and no-go results are unchanged. Its capacity-interpretation language is qualified because a separate judgment now accepts the same decimal as a valid UV-derived converse; the coarse-relaxation witness itself still supplies no capacity bound.

## Node: programs/dependence_balance_entropy_relaxation/coarse_entropy_counterfeit

- **Title:** Finite entropic counterfeit for the specified coarse BSSC relaxation
- **Type:** Constructive relaxation result
- **Status:** Active
- **Parent:** `programs/dependence_balance_entropy_relaxation`

### Current knowledge

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` accepts with high confidence an actual finite joint distribution satisfying the specified coarse BSSC entropy relaxation and attaining

\[
B_1=B_2
=2h_2(1/4)-\frac54
=0.3725562489182657\ldots.
\]

Let

\[
h=h_2(1/4),\qquad
s=1-h,\qquad
r=h-\frac34,\qquad
t=2r.
\]

The accepted witness uses mutually independent binary components

\[
C,A,B1c,B2c,Eu,Ev,Ny,Nz
\]

with respective entropies

\[
t,\quad
s,\quad
r,\quad
s-r,\quad
\frac12-r,\quad
r,\quad
\frac12,\quad
\frac12.
\]

Its tuple variables are

\[
U=(C,A,B2c,Eu),
\qquad
V=(B1c,Ev),
\]

\[
X=(C,A,B1c,B2c,Eu,Ev),
\]

\[
Y=(C,A,Ny),
\qquad
Z=(C,B1c,B2c,Nz),
\]

with \(W,T\) constant.

The judgment accepts the base entropy vector

\[
H(X)=1,
\qquad
H(Y)=H(Z)=h,
\]

\[
H(X,Y)=H(X,Z)=H(Y,Z)=\frac32,
\qquad
H(X,Y,Z)=2.
\]

It also accepts that:

- \(U\) and \(V\) consist of disjoint independent components;
- \(U,V\) together determine \(X\);
- conditional on \(X\), only the independent output-noise components remain;
- the joint output reveals exactly half the entropy of each of \(U\) and \(V\);
- all stated disjoint-subtuple BEC identities hold, including the 65 nonempty-left-subtuple cases; and
- both scalar support rows are tight.

The accepted component accounting gives

\[
I(U;Y)=I(X;Y\mid V)=h-\frac12
\]

and

\[
I(X;Z\mid U)=I(V;Z)=r.
\]

Consequently,

\[
B_1=B_2
=\left(h-\frac12\right)+r
=2h-\frac54.
\]

The judgment emphasizes that this is an actual finite distribution rather than an abstract polymatroid or sampled entropy vector. An exact formal-entropy checker using rational coefficients in the formal parameter \(h\) corroborates the component bookkeeping and the 65 disjoint-subtuple identities.

The mathematical interpretation remains specific:

- the witness proves that the specified coarse relaxation can attain
  \[
  2h_2(1/4)-\frac54;
  \]
- the witness and that coarse formulation alone provide neither a lower nor an upper bound on the actual BSSC capacity;
- they do not determine \(C_{\mathrm{sum}}\);
- they do not improve or contradict the governed capacity frontier.

Primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` separately accepts the same numerical value as a valid branchwise-relaxed UV converse. That is a distinct derivation in a different program. It does not alter what the entropic counterfeit establishes or turn the counterfeit into a capacity certificate.

### Provenance

- **Claim key:** `coarse-bssc-entropy-relaxation-entropic-counterfeit`
- **Capacity-interpretation claim key:** `coarse-bssc-entropy-relaxation-value-capacity-interpretation`
- **Principal subject transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Context transactions:**  
  `d638c346212db3e75f6a53dcebcfd09f55125852`  
  `7e7626cbff7270572d51a8fda719154ab602907f`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **UV-interpretation context transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **UV-interpretation judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation/coarse_entropy_counterfeit

The counterfeit construction and its accepted accounting are unchanged. The node now expressly distinguishes the witness’s non-capacity interpretation from the separate UV judgment that derives the same number as a valid but weaker upper bound.

## Node: programs/uv_relaxed_scalar

- **Title:** Tensorization and symmetry of separately relaxed UV sum-rate scalars
- **Type:** Program
- **Status:** Active
- **Parent:** `root`

### Current knowledge

This program studies two separately relaxed UV sum-rate scalar functionals for finite-alphabet broadcast channels.

For a channel \(W:X\to(Y,Z)\) and input law \(p\), define

\[
t_W(p)=I_p(X;Y)-I_p(X;Z),
\]

and let \(\mathfrak C[f]\) denote the upper concave envelope of \(f\) over input laws. Define the two scalar branches

\[
A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),
\]

\[
D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p).
\]

The averaged and branchwise channel functionals are

\[
B_{\mathrm{avg}}(W)
=\sup_p\frac{A_W(p)+D_W(p)}2
\]

and

\[
B_{\mathrm{br}}(W)
=\sup_p\min\{A_W(p),D_W(p)\}.
\]

Primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` accepts the following theorem chain:

1. For arbitrary finite-alphabet broadcast channels,
   \[
   B_{\mathrm{avg}}(W_1\times W_2)
   =B_{\mathrm{avg}}(W_1)+B_{\mathrm{avg}}(W_2).
   \]
   The conclusion includes correlated product-channel inputs and envelope auxiliaries that range jointly across factors.

2. If a channel is receiver-skew-symmetric, then
   \[
   B_{\mathrm{br}}(W)=B_{\mathrm{avg}}(W),
   \]
   and the optimization may be restricted to input laws invariant under the symmetry.

3. For every finite product of receiver-skew-symmetric finite-alphabet channels,
   \[
   B_{\mathrm{br}}\!\left(\prod_i W_i\right)
   =\sum_i B_{\mathrm{br}}(W_i).
   \]

4. For the half-skew BSSC \(P\),
   \[
   B_{\mathrm{br}}(P)=B_{\mathrm{avg}}(P)
   =2h_2(1/4)-\frac54,
   \]
   and for every finite \(n\ge1\),
   \[
   B_{\mathrm{br}}(P^{\times n})
   =B_{\mathrm{avg}}(P^{\times n})
   =n\left(2h_2(1/4)-\frac54\right).
   \]

5. The branchwise scalar supplies a valid relaxed UV sum-rate converse. For the BSSC this yields
   \[
   C_{\mathrm{sum}}
   \le 2h_2(1/4)-\frac54
   =0.3725562489182657\ldots.
   \]

The BSSC bound is noncompetitive. It is larger, and therefore weaker, than the published benchmark upper endpoint \(0.369316568803963\) and the governed continuous full-Theorem-9 fixed-pair bound \(0.369296945969202842443\). It changes neither the current lower bound nor the current upper frontier and is not achievable-rate evidence.

### Scope boundaries

The accepted results concern scalar functionals built from separately optimized upper concave envelopes. They do not establish additivity or equivalence for:

- the complete UV outer region;
- formulations retaining one common joint \((U,V)\) law for both rows;
- arbitrary weighted UV scalarizations;
- the simplified Gohari–Liu–Nair functional;
- the full Gohari–Liu–Nair Theorem 9 bound; or
- nonsymmetric channels in the branch-average equality statement.

Thus the program closes the specified finite-product route through the separately relaxed scalars, not tensorization of stronger converse regions.

### Program nodes

- `programs/uv_relaxed_scalar/averaged_product_additivity`
- `programs/uv_relaxed_scalar/skew_symmetry_branch_average`
- `programs/uv_relaxed_scalar/skew_symmetric_branchwise_product_additivity`
- `programs/uv_relaxed_scalar/half_skew_bssc_exact_value`

### Credit and provenance

The primary judgment records the subject as an attributed port of earlier accepted artifacts. Mathematical authorship is attributed to Robert Raynor, and the port disclaims new authorship of the original results.

The judgment distinguishes two contributions:

1. exact product additivity of the averaged separately relaxed UV scalar; and
2. the symmetry argument identifying the branchwise and averaged scalars and transferring additivity to the branchwise functional.

The exact BSSC specialization additionally uses the sharp posterior-support calculation from transaction `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`; that supporting calculation is distinct from the tensorization and symmetry arguments.

- **Subject transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **Primary judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Supporting transactions:**  
  `d638c346212db3e75f6a53dcebcfd09f55125852`  
  `7e7626cbff7270572d51a8fda719154ab602907f`  
  `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Judgment disposition:** Accepted as a correct structural contribution
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/uv_relaxed_scalar

A new top-level program is created because tensorization, receiver-skew symmetry, and exact evaluation of the separately relaxed UV scalars form an independent long-lived research agenda rather than a submission-shaped event or a subtopic of the existing auxiliary-receiver and entropy-relaxation programs.

## Node: programs/uv_relaxed_scalar/averaged_product_additivity

- **Title:** Exact product additivity of the averaged separately relaxed UV scalar
- **Type:** Structural theorem
- **Status:** Active
- **Parent:** `programs/uv_relaxed_scalar`

### Current knowledge

For a finite-alphabet broadcast channel \(W\), define

\[
t_W(p)=I_p(X;Y)-I_p(X;Z),
\]

\[
A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),
\qquad
D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p),
\]

and

\[
B_{\mathrm{avg}}(W)
=\sup_p\frac{A_W(p)+D_W(p)}2.
\]

Primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` accepts with high confidence that for arbitrary finite-alphabet broadcast channels \(W_1,W_2\),

\[
\boxed{
B_{\mathrm{avg}}(W_1\times W_2)
=
B_{\mathrm{avg}}(W_1)+B_{\mathrm{avg}}(W_2)
}.
\]

The theorem covers arbitrarily correlated input laws on the product channel. It also permits concave-envelope auxiliaries joint across the two factors; the upper-bound direction does not impose a hidden product-input restriction.

The accepted reverse direction uses product input laws and independent posterior decompositions approaching the separately optimized envelope values. No common auxiliary for the \(t\) and \(-t\) envelopes is asserted or required because the definition of \(B_{\mathrm{avg}}\) optimizes those envelopes separately.

The judgment treats the analytic chain-rule and concave-envelope argument as decisive. Accompanying numerical experiments are corroborative rather than necessary evidence.

### Scope boundaries

This exact additivity result does not imply product additivity of:

- the complete UV rate region;
- a scalar retaining a common joint law for both UV auxiliaries;
- arbitrary weighted UV scalarizations;
- the simplified Gohari–Liu–Nair functional; or
- the full Gohari–Liu–Nair Theorem 9 outer bound.

### Credit and provenance

The primary judgment attributes mathematical authorship to Robert Raynor and records the subject as an attributed port that disclaims new authorship.

- **Claim key:** `uv-averaged-functional-product-additivity`
- **Subject transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **Context transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Primary judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Judgment stance:** Supported with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/uv_relaxed_scalar/averaged_product_additivity

This new result node materializes the accepted exact tensorization theorem for \(B_{\mathrm{avg}}\), including its correlated-input generality and the judgment’s explicit exclusions from stronger UV and Gohari–Liu–Nair formulations.

## Node: programs/uv_relaxed_scalar/skew_symmetry_branch_average

- **Title:** Equality of branchwise and averaged UV scalars under receiver-skew symmetry
- **Type:** Symmetry theorem
- **Status:** Active
- **Parent:** `programs/uv_relaxed_scalar`

### Current knowledge

Let

\[
B_{\mathrm{avg}}(W)
=\sup_p\frac{A_W(p)+D_W(p)}2
\]

and

\[
B_{\mathrm{br}}(W)
=\sup_p\min\{A_W(p),D_W(p)\},
\]

where \(A_W,D_W\) are the separately relaxed UV branches.

Suppose a finite-alphabet broadcast channel has an involutive input relabeling \(S\) that exchanges the two receiver channels up to bijective output relabeling. Primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` accepts with high confidence that

\[
\boxed{
B_{\mathrm{br}}(W)=B_{\mathrm{avg}}(W)
}.
\]

The optimization may be restricted to \(S\)-invariant input laws.

The accepted result uses covariance of the two scalar branches under receiver exchange and concavity under symmetrization. At an invariant input law, the two branches agree. The conclusion does not require the input alphabet to be binary.

### Scope boundaries

The theorem does not establish:

- the same equality for nonsymmetric channels;
- a simultaneous common-\((U,V)\) representation of the two separately relaxed rows; or
- equality between these scalars and stronger UV or Gohari–Liu–Nair outer-bound formulations.

### Credit and provenance

The primary judgment attributes the symmetry contribution to Robert Raynor and records the subject as an attributed port.

- **Claim key:** `receiver-skew-symmetric-uv-branch-average-equality`
- **Subject transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **Context transaction:** `7e7626cbff7270572d51a8fda719154ab602907f`
- **Primary judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Judgment stance:** Supported with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/uv_relaxed_scalar/skew_symmetry_branch_average

This new node records the accepted symmetry reduction as a durable theorem distinct from product additivity, including the invariant-prior restriction and the judgment’s prohibition on extending it to common-auxiliary or nonsymmetric formulations.

## Node: programs/uv_relaxed_scalar/skew_symmetric_branchwise_product_additivity

- **Title:** Product additivity of the branchwise scalar for receiver-skew-symmetric channels
- **Type:** Tensorization theorem
- **Status:** Active
- **Parent:** `programs/uv_relaxed_scalar`

### Current knowledge

For every finite family of receiver-skew-symmetric finite-alphabet broadcast channels \(W_1,\ldots,W_n\), primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` accepts with high confidence that

\[
\boxed{
B_{\mathrm{br}}\!\left(\prod_{i=1}^n W_i\right)
=
\sum_{i=1}^n B_{\mathrm{br}}(W_i)
}.
\]

The product channel remains receiver-skew-symmetric under coordinatewise input involutions and output relabelings. The accepted theorem is a dependency-ordered consequence of:

- exact additivity of \(B_{\mathrm{avg}}\) for arbitrary finite-alphabet product channels; and
- equality \(B_{\mathrm{br}}=B_{\mathrm{avg}}\) on receiver-skew-symmetric channels.

The theorem inherits the generality of the averaged additivity result: correlated input laws on the product channel are permitted, and there is no hidden product-input restriction.

### Scope boundaries

The result is product additivity of the specified branchwise scalar, not tensorization of:

- the complete UV outer region;
- a common-joint-\((U,V)\) formulation;
- the simplified Gohari–Liu–Nair functional; or
- the full Theorem 9 outer-bound system.

It also does not establish branchwise additivity for arbitrary nonsymmetric factors.

### Credit and provenance

The primary judgment attributes the underlying tensorization and symmetry results to Robert Raynor and records the subject as an attributed port.

- **Claim key:** `receiver-skew-symmetric-uv-branchwise-product-additivity`
- **Subject transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **Context transactions:**  
  `d638c346212db3e75f6a53dcebcfd09f55125852`  
  `7e7626cbff7270572d51a8fda719154ab602907f`
- **Primary judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Judgment stance:** Supported with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/uv_relaxed_scalar/skew_symmetric_branchwise_product_additivity

This new node preserves the accepted branchwise tensorization theorem separately from its averaged-additivity and symmetry dependencies, while retaining the judgment’s restrictions against interpreting it as tensorization of stronger converse regions.

## Node: programs/uv_relaxed_scalar/half_skew_bssc_exact_value

- **Title:** Exact half-skew BSSC value of the separately relaxed UV scalars
- **Type:** Exact evaluation and converse result
- **Status:** Active
- **Parent:** `programs/uv_relaxed_scalar`

### Current knowledge

For the half-skew BSSC \(P\), primary judgment `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318` accepts with high confidence that

\[
\boxed{
B_{\mathrm{br}}(P)=B_{\mathrm{avg}}(P)
=
2h_2(1/4)-\frac54
}.
\]

Numerically,

\[
2h_2(1/4)-\frac54
=0.3725562489182657\ldots.
\]

The input flip \(x\mapsto1-x\), together with output flips, exchanges the two BSSC receiver marginals. Thus the channel satisfies the receiver-skew-symmetry condition. For the one-letter binary input, the invariant input law is the fair prior \(q=1/2\).

Writing

\[
h=h_2(1/4),\qquad
c=h-\frac12,\qquad
r=h-\frac34,
\]

the accepted specialization has

\[
I_Y(1/2)=I_Z(1/2)=c
\]

and

\[
\mathfrak C[t](1/2)
=\mathfrak C[-t](1/2)
=r.
\]

The exact envelope value uses the sharp BSSC posterior support accepted in the earlier dependence-balance and entropy-relaxation judgment. The equality-achieving posterior mixture recorded by the UV judgment is

\[
\frac58\delta_{4/5}+\frac38\delta_0
\]

for the relevant orientation, with reflection supplying the opposite branch. Consequently,

\[
A_P(1/2)=D_P(1/2)=c+r
=2h_2(1/4)-\frac54.
\]

For every finite \(n\ge1\), the accepted tensorization results give

\[
\boxed{
B_{\mathrm{br}}(P^{\times n})
=
B_{\mathrm{avg}}(P^{\times n})
=
n\left(2h_2(1/4)-\frac54\right)
}.
\]

The branchwise scalar is a valid relaxed UV sum-rate converse, so the evaluation yields

\[
C_{\mathrm{sum}}
\le 2h_2(1/4)-\frac54.
\]

This is not a new frontier bound. It is weaker than

\[
C_{\mathrm{sum}}\le0.369316568803963
\]

and weaker than the governed continuous fixed-pair certificate

\[
C_{\mathrm{sum}}\le0.369296945969202842443.
\]

It therefore changes neither the governed capacity interval nor the unresolved status of the exact sum-capacity. It is not evidence of achievability.

The same numerical value also occurs as the objective attained by the finite counterfeit in the specified coarse entropy relaxation. That separate occurrence is not itself a capacity bound and is not the source of the UV converse.

### Scope boundaries

The exact finite-block scalar evaluation does not establish:

- the exact BSSC sum-capacity;
- a matching achievable rate;
- tensorization of the complete UV outer region;
- tensorization of the simplified Gohari–Liu–Nair functional;
- tensorization of the full Theorem 9 system; or
- equality between this relaxed scalar and any stronger converse.

### Credit and provenance

The primary judgment attributes the tensorization and symmetry arguments to Robert Raynor and records the subject as an attributed port. It separately identifies the sharp posterior-support calculation from the earlier dependence-balance transaction as supporting the exact BSSC specialization.

- **Exact-value claim key:** `half-skew-bssc-uv-relaxed-scalar-value`
- **Converse-interpretation claim key:** `half-skew-bssc-uv-relaxed-converse-does-not-improve-frontier`
- **Subject transaction:** `f236017c62c67ce4218c1f81ea34134f0954b556`
- **Supporting transactions:**  
  `d638c346212db3e75f6a53dcebcfd09f55125852`  
  `7e7626cbff7270572d51a8fda719154ab602907f`  
  `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Primary judgment:** `sha256:0534c0e3521650e63989cffa2530883e74095b980b811738b6f696919c77b318`
- **Judgment stance:** Exact scalar value supported with high confidence; converse interpretation accepted
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/uv_relaxed_scalar/half_skew_bssc_exact_value

This new node records the accepted exact one-letter and finite-product evaluations, their reliance on the earlier posterior-support result, and the separate judgment that the resulting UV converse is valid but strictly weaker than the governed capacity upper bound.
