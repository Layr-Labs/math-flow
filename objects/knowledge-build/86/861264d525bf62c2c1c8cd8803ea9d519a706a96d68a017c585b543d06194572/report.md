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

The governed current benchmark remains

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

According to that judgment, this converse comes from the full Gohari–Liu–Nair Theorem 9 outer bound at one specified reflected binary auxiliary-receiver pair. Its certificate uses an exact nonnegative six-row dual combination, outward-rounded interval majorants over the complete posterior interval \([0,1]\), and analytic maximization over every input prior. It is not merely a finite posterior-grid calculation.

The exact value of \(C_{\mathrm{sum}}\) remains unknown. The accepted fixed-pair certificate does not establish matching achievability, global optimality of the selected auxiliary-receiver pair, global sufficiency of binary or reflected auxiliary receivers, global optimality of the selected six-row dual face, or certification of the smaller numerical lead

\[
0.369296340638082.
\]

The earlier exact three-point-grid result remains a lower approximation to a fixed-receiver outer-bound functional rather than a capacity upper bound. The earlier midpoint-localization result remains a necessary localization statement relative to its supplied threshold. Neither determines the global auxiliary-receiver optimization.

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` accepts, with high confidence and within an explicitly limited scope, a separate structural line concerning:

- an exact finite-block dependence-balance telescope;
- selected-coordinate fixed-map factorization and four rate inequalities;
- a sharp scalar BSSC posterior-support inequality;
- an actual finite entropic counterfeit for a specified coarse entropy relaxation; and
- a no-go result for strengthening that particular relaxation with universally valid finite-variable information inequalities or finitely many standard copy-lemma extensions.

That judgment expressly finds that these results do not determine the BSSC sum-capacity or improve either endpoint of the governed numerical interval. In particular,

\[
2h_2(1/4)-\frac54
=0.3725562489182657\ldots
\]

is only an objective value of the specified deliberately over-relaxed entropy formulation. It is neither a lower nor an upper bound on the actual BSSC capacity and does not conflict with the smaller certified fixed-pair capacity upper bound.

### Durable program structure

The durable programs directly beneath the root are:

- `programs/auxiliary_receiver_outer_bound` — structural reductions, finite-grid analysis, continuous fixed-pair converses, exact dual-functional identities, certificate reproducibility, and the unresolved global auxiliary-receiver optimization associated with the Gohari–Liu–Nair outer bound.
- `programs/dependence_balance_entropy_relaxation` — finite-block dependence-balance and selected-coordinate structure, together with BSSC-specific analysis of the capabilities and limitations of a specified coarse entropy relaxation.

No conflict or reconciliation records were supplied. The remaining limitations are open mathematical or evidentiary dependencies, not disputes between opposed primary judgments.

### Provenance

- **Lower-bound source:** Supplied problem statement
- **Earlier subject transaction:** `d638c346212db3e75f6a53dcebcfd09f55125852`
- **Earlier primary judgment:** `sha256:5e3cc6409a4bd37685561d3bf00cb162be0b060f12b942a0ba346cd4c8cf0f99`
- **Fixed-pair subject transaction:** `7e7626cbff7270572d51a8fda719154ab602907f`
- **Fixed-pair primary judgment:** `sha256:7900cd147fe7e4ff768646a2ed7a0ad6e9afa8d92e904fe8f62aa4af756c6a44`
- **Dependence-balance and entropy-relaxation subject transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Dependence-balance and entropy-relaxation primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Conflict status:** No supplied conflict or reconciliation records

## Change: root

The root is extended to recognize the new durable dependence-balance and entropy-relaxation program. The numerical capacity frontier and exact-value status are unchanged because the new primary judgment expressly disclaims any capacity-bound improvement and classifies its numerical relaxation value as neither a lower nor an upper bound.

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
- a selected-coordinate factorization retaining the stronger property \(X=f_T(U,V)\), independent of the selected state \(W\); and
- two individual-rate and two sum-rate inequalities compatible with that factorization.

These conclusions remain sequence-level. The judgment finds that no simultaneous cardinality or compactness reduction has been established, so arbitrary optimization over small auxiliary alphabets would not certify a universal converse.

For the second agenda, the judgment accepts with high confidence:

- a global affine support for the fair-input BSSC posterior-information difference, sharp in its stated scalar direction;
- an actual finite joint distribution satisfying the specified structural, entropy, disjoint-subtuple BEC, and support constraints of the coarse relaxation;
- the relaxation objective value
  \[
  2h_2(1/4)-\frac54
  =0.3725562489182657\ldots;
  \]
- exact component accounting, corroborated by a formal-entropy checker; and
- the conclusion that universal finite-variable information inequalities and any finite sequence of standard copy-lemma extensions cannot exclude this witness or force this particular relaxation below that value.

The no-go conclusion is restricted to the specified relaxation and the named universal-inequality/copy-lemma strengthening methods. The objective value is not a capacity bound, and the program currently provides no improvement to the global BSSC sum-capacity interval.

### Program nodes

- `programs/dependence_balance_entropy_relaxation/finite_block_telescope`
- `programs/dependence_balance_entropy_relaxation/selected_coordinate_constraints`
- `programs/dependence_balance_entropy_relaxation/uniform_bssc_posterior_support`
- `programs/dependence_balance_entropy_relaxation/coarse_entropy_counterfeit`
- `programs/dependence_balance_entropy_relaxation/universal_inequality_copy_no_go`

### Provenance

- **Subject transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Judgment stance:** Accepted within explicitly limited scope; individual structural findings accepted with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation

This durable program is created because the accepted finite-block dependence-balance line and the scoped entropy-relaxation obstruction form a continuing research agenda independent of the existing auxiliary-receiver outer-bound program. Its identity does not depend on the submission’s transaction name or chronology.

## Node: programs/dependence_balance_entropy_relaxation/finite_block_telescope

- **Title:** Exact finite-block private-message dependence-balance telescope
- **Type:** Structural result
- **Status:** Active
- **Parent:** `programs/dependence_balance_entropy_relaxation`

### Current knowledge

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` accepts this result with high confidence.

For independent private messages \(A,B\), a deterministic length-\(n\) encoder, and

\[
S_i=(Y^{i-1},Z_{i+1}^n),
\]

the accepted exact identity is

\[
\sum_{i=1}^n
\left[
I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)
\right]
=
I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]

If \(F_1,F_2\) are the corresponding Fano quantities and

\[
\delta_j=\frac{F_j}{n},
\]

the accepted finite-block estimate is

\[
\left|
\frac1n\sum_{i=1}^n
\left[
I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)
\right]
\right|
\le \max\{\delta_1,\delta_2\}.
\]

With a uniform independent time \(T\) and

\[
U=A,\qquad V=B,\qquad W=S_T,\qquad Y=Y_T,\qquad Z=Z_T,
\]

the selected-coordinate condition is

\[
\left|
I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)
\right|
\le \max\{\delta_1,\delta_2\}.
\]

According to the judgment, \(\delta_1,\delta_2\to0\) along reliable bounded-rate code sequences. Thus the selected-coordinate dependence-balance defect vanishes along such sequences.

The judgment also preserves a decisive limitation: the induced alphabets of \(U,V,W\) may grow with blocklength. The vanishing scalar defect is therefore a sequence-level condition and does not itself produce a compact fixed-alphabet single-letter outer region.

The judgment attributes the exact telescope to the quantities

\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),
\]

whose consecutive differences are the displayed summands, and attributes the endpoint estimate to Fano bounds. These are recorded as the judgment’s proof basis rather than independently reassessed here.

### Provenance

- **Claim key:** `finite-block-private-message-dependence-balance-telescope`
- **Subject and evidence transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Judgment stance:** Supports; accepted with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation/finite_block_telescope

This node is created to preserve the accepted exact telescope and its vanishing-defect consequence as a durable finite-block structural result. Its explicit sequence-level limitation is retained because the judgment does not supply a fixed-alphabet compactness theorem.

## Node: programs/dependence_balance_entropy_relaxation/selected_coordinate_constraints

- **Title:** Selected-coordinate fixed-map factorization and rate constraints
- **Type:** Structural outer constraints
- **Status:** Active
- **Parent:** `programs/dependence_balance_entropy_relaxation`

### Current knowledge

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` accepts this result with high confidence.

For the selected-coordinate variables

\[
U=A,\qquad V=B,\qquad W=(Y^{T-1},Z_{T+1}^n),
\]

with \(T\) uniform and independent, every deterministic private-message code induces the factorization

\[
p(t,u,v,w,x,y,z)
=
\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf 1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x).
\]

The accepted factorization retains the stronger fixed-map property

\[
X=f_T(U,V),
\qquad\text{equivalently}\qquad
H(X\mid U,V,T)=0.
\]

In particular, the encoder map at time \(T\) does not depend on the realized state \(W\). The judgment distinguishes this from the weaker relaxation \(H(X\mid U,V,W,T)=0\), which would allow \(W\) to select among different encoder maps.

The following four finite-block inequalities are accepted:

\[
R_1\le I(U,W;Y\mid T)+\delta_1,
\]

\[
R_2\le I(V,W;Z\mid T)+\delta_2,
\]

\[
R_1+R_2
\le I(U,W;Y\mid T)
   +I(X;Z\mid U,W,T)
   +\delta_1+\delta_2,
\]

and

\[
R_1+R_2
\le I(V,W;Z\mid T)
   +I(X;Y\mid V,W,T)
   +\delta_1+\delta_2.
\]

The judgment attributes these rows to Fano’s inequality, the forward and reverse chain rules, memorylessness, deterministic encoding, and conditioned Csiszár sum identities. It reports that only nonnegative remainder terms are discarded in deriving the two sum-rate rows.

No simultaneous cardinality or compactness reduction for \(U,V,W,T\) is established. Consequently, the judgment expressly warns that optimizing these constraints over arbitrarily selected small alphabets would not certify a universal capacity converse.

### Provenance

- **Claim key:** `selected-coordinate-fixed-map-factorization-and-rate-inequalities`
- **Subject and evidence transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Judgment stance:** Supports; accepted with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation/selected_coordinate_constraints

This node is created for the accepted fixed-map factorization and its four associated rate rows. It remains separate from the telescope because it records encoder structure and rate constraints, while preserving the judgment’s unresolved cardinality and compactness limitation.

## Node: programs/dependence_balance_entropy_relaxation/uniform_bssc_posterior_support

- **Title:** Sharp fair-input BSSC posterior-difference support
- **Type:** Analytic lemma
- **Status:** Active
- **Parent:** `programs/dependence_balance_entropy_relaxation`

### Current knowledge

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` accepts this analytic result with high confidence.

Let

\[
h=h_2(1/4),
\qquad
r=h-\frac34,
\]

and let

\[
g(q)=I_Z(q)-I_Y(q)
\]

denote the difference between the two BSSC marginal mutual informations when \(P(X=1)=q\). The accepted global affine support is

\[
g(q)\le 2r(1-q),
\qquad 0\le q\le1.
\]

The judgment records exact tangent contact at

\[
q=\frac15,
\qquad
g\!\left(\frac15\right)=\frac85r,
\qquad
g'\!\left(\frac15\right)=-2r.
\]

For fair input and every auxiliary satisfying \(A-X-(Y,Z)\), the support yields the accepted scalar inequality

\[
I(X;Z\mid A)-I(X;Y\mid A)\le r.
\]

The reflected inequality holds with the same right-hand side.

The constant is sharp in this scalar direction: the judgment accepts equality for the posterior mixture placing probability \(5/8\) at \(q=1/5\) and probability \(3/8\) at \(q=1\), whose mean posterior is \(1/2\).

The judgment characterizes this as a globally proved analytic support rather than a numerical-grid observation. Its scope is the stated fair-input scalar posterior direction; it is not itself a capacity theorem.

### Provenance

- **Claim key:** `uniform-bssc-posterior-difference-support-at-r`
- **Subject and evidence transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Judgment stance:** Supports; accepted with high confidence
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation/uniform_bssc_posterior_support

This node is created because the global affine support and its sharpness form a durable BSSC-specific analytic lemma used by the coarse entropy-relaxation analysis. Its scalar and fair-input scope is retained exactly as judged.

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

The tuple variables are

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

The judgment accepts the following base entropy vector:

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
- all stated disjoint-subtuple BEC identities hold, with 65 nonempty-left-subtuple cases; and
- both scalar support rows are tight.

The accepted component accounting gives

\[
I(U;Y)=I(X;Y\mid V)=h-\frac12,
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

The judgment emphasizes that this is an actual finite distribution, not an abstract polymatroid or a sampled entropy vector. An exact formal-entropy checker using rational coefficients in the formal parameter \(h\) credibly corroborates the component bookkeeping, including the 65 disjoint-subtuple identities.

The value

\[
2h_2(1/4)-\frac54
\]

is only the objective value of the deliberately over-relaxed formulation. The judgment expressly finds that it is neither a lower nor an upper bound on the actual BSSC capacity, does not determine \(C_{\mathrm{sum}}\), and does not improve or contradict the governed capacity frontier.

### Provenance

- **Claim key:** `coarse-bssc-entropy-relaxation-entropic-counterfeit`
- **Capacity-interpretation claim key:** `coarse-bssc-entropy-relaxation-value-capacity-interpretation`
- **Subject and principal evidence transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Context transactions for capacity interpretation:**  
  `d638c346212db3e75f6a53dcebcfd09f55125852`  
  `7e7626cbff7270572d51a8fda719154ab602907f`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Judgment stance:** Witness supported and accepted with high confidence; capacity interpretation qualified
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation/coarse_entropy_counterfeit

This node is created for the accepted finite witness and its exact relaxation objective. The node incorporates the judgment’s mandatory qualification that the value is not a BSSC capacity bound, preventing the over-relaxed objective from being confused with the global numerical frontier.

## Node: programs/dependence_balance_entropy_relaxation/universal_inequality_copy_no_go

- **Title:** Universal-information-inequality and finite-copy no-go for the coarse relaxation
- **Type:** Scoped methodology limitation
- **Status:** Active
- **Parent:** `programs/dependence_balance_entropy_relaxation`

### Current knowledge

Primary judgment `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f` supports the following scoped obstruction.

Because the entropic counterfeit in `programs/dependence_balance_entropy_relaxation/coarse_entropy_counterfeit` is an actual finite joint distribution, it satisfies every universally valid finite-variable information inequality, including non-Shannon inequalities.

The judgment further accepts that standard copy-lemma extensions can be realized for this witness by the required conditional resampling. Therefore, no finite sequence of such standard copy-lemma extensions can exclude the witness.

Consequently, neither:

- adding universally valid finite-variable information inequalities, nor
- adding any finite sequence of standard copy-lemma extensions

can force the specified coarse entropy relaxation below

\[
2h_2(1/4)-\frac54.
\]

This conclusion is limited to the specified coarse relaxation and the named universal-information-inequality and finite-copy strengthening methods. It does not determine the BSSC sum-capacity, does not turn the relaxation value into a capacity bound, and does not rule out converse methods outside that stated scope.

### Provenance

- **Claim key:** `universal-information-inequality-and-finite-copy-no-go-for-specified-relaxation`
- **Subject and evidence transaction:** `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6`
- **Primary judgment:** `sha256:dd536a4c3d9fc68fdf3768af2fc9d9f0bedef487a207375d7820bfc6c49ed99f`
- **Judgment stance:** Supports, with the obstruction explicitly limited to the specified relaxation and methods
- **Conflict status:** No supplied conflict or reconciliation records

## Change: programs/dependence_balance_entropy_relaxation/universal_inequality_copy_no_go

This node is created to preserve the accepted methodology limitation separately from the witness that establishes it. The node retains the judgment’s narrow scope and does not generalize the obstruction to other relaxations, converse techniques, or the capacity problem itself.
