# Code-induced dependence balance and its entropy/copy obstruction

## Claims and exact scope

This is an attributed, independently audited port of the consecutive accepted
Yukon artifacts `upper-dependence-balance` and `upper-entropy-nogo`.  They form
one dependency-complete structural result: the first derives a necessary
condition from every deterministic private-message code, and the second proves
that a specified entropy-only relaxation of that condition cannot improve the
classical UV value.

### Finite-block code-induced balance

Let (A) and (B) be independent uniform private messages, encoded
deterministically over (n) uses of a finite-alphabet memoryless broadcast
channel.  Receiver (Y) estimates (A) with average error (p_1), and
receiver (Z) estimates (B) with error (p_2).  Define

\[
F_j=h_2(p_j)+p_j\log_2(N_j-1),\qquad \delta_j=F_j/n.
\]

For

\[
S_i=(Y^{i-1},Z_{i+1}^n),
\]

the exact telescope is

\[
\sum_{i=1}^n
\left[I(A;B\mid S_i,Y_i)-I(A;B\mid S_i,Z_i)\right]
=I(A;B\mid Y^n)-I(A;B\mid Z^n).
\]

Both endpoints are nonnegative, while Fano bounds them by (F_1) and
(F_2), respectively.  With independent uniform time (T), and

\[
U=A,\quad V=B,\quad W=S_T,\quad X=X_T,\quad Y=Y_T,\quad Z=Z_T,
\]

every such code therefore induces

\[
\left|I(U;V\mid W,T,Y)-I(U;V\mid W,T,Z)\right|
\le\max\{\delta_1,\delta_2\}.
\]

The complete induced law retains the fixed coordinate map:

\[
p(t,u,v,w,x,y,z)=\frac1n p_U(u)p_V(v)p(w\mid u,v,t)
\mathbf 1\{x=f_t(u,v)\}P_{YZ\mid X}(y,z\mid x).
\]

In particular, (U\perp V), (T\perp(U,V)), (X=f_T(U,V)), and the
realized state (W) cannot select another encoder map after (u,v,t) are
fixed.  The same variables satisfy four compatible rate rows:

\[
\begin{aligned}
R_1&\le I(U,W;Y\mid T)+\delta_1,\\
R_2&\le I(V,W;Z\mid T)+\delta_2,\\
R_1+R_2&\le I(U,W;Y\mid T)+I(X;Z\mid U,W,T)+\delta_1+\delta_2,\\
R_1+R_2&\le I(V,W;Z\mid T)+I(X;Y\mid V,W,T)+\delta_1+\delta_2.
\end{aligned}
\]

This is an exact sequence-level necessary condition.  The alphabets of the
messages and (W) grow with blocklength, so it is not by itself a fixed-
cardinality single-letter outer region.

### Exact entropy/copy no-go theorem

At uniform input, put

\[
h=h_2(1/4),\qquad c=h-1/2,\qquad r=h-3/4.
\]

Consider the coarse entropy relaxation that imposes:

- the complete seven nonempty entropies of the common-noise BSSC coupling,
  namely (H(X)=1), (H(Y)=H(Z)=h),
  (H(X,Y)=H(X,Z)=H(Y,Z)=3/2), and (H(X,Y,Z)=2);
- message/time independence, deterministic encoding, the fixed-map equality,
  the memoryless Markov equality, and exact dependence balance;
- every conditional BEC identity
  (I(L;Y,Z\mid K)=\tfrac12I(L;X\mid K)) for disjoint subtuples
  (L,K\subseteq\{U,V,W,T\}), with (L\ne\varnothing);
- the two sharp scalar BSSC posterior-support inequalities with right side
  (r).

There is an actual finite entropic point satisfying all these constraints for
which both direct sum branches equal

\[
\boxed{2h_2(1/4)-\frac54
=0.3725562489182657\ldots}.
\]

Consequently, adding any collection of universally valid finite-variable
information inequalities, including unknown non-Shannon inequalities, cannot
lower this relaxation below that value.  Nor can any finite sequence of
standard copy-lemma extensions: each copy step can be realized by conditional
resampling of the finite witness while preserving its original marginal and
objective.

The witness is deliberately not a binary BSSC distribution.  Its (X) is a
tuple of six nondegenerate independent binary components.  Exact binary-
posterior or other channel-specific consistency constraints exclude it and
remain viable.  The theorem obstructs only the stated entropy/copy refinement
route.

## Independent proof audit

For the balance theorem, set

\[
D_i=I(A;B\mid Y^i,Z_{i+1}^n),\qquad 0\le i\le n.
\]

The (i)-th balance summand is exactly (D_i-D_{i-1}), so no channel
inequality is hidden in the telescope.  Separate reliability bounds the two
endpoints.  The displayed fixed-map factorization follows because, conditional
on (A,B,T), the current input is fixed and the current memoryless output is
independent of the past/future outputs in (W).  The two sum-rate rows use the
conditioned Csiszar identity; their uncancelled remainders are respectively
(sum_i I(Y^{i-1};Y_i)) and
(sum_i I(Z_{i+1}^n;Z_i)), hence nonnegative.

For the no-go theorem, write (g(q)=I_Z(q)-I_Y(q)).  Direct differentiation
gives

\[
g''(q)=\frac{2q-1}{\ln(2)q(1-q)(1+q)(2-q)}.
\]

Thus (g) is concave to (1/2) and convex thereafter.  The exact identities

\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r
\]

show that the tangent (2r(1-q)) is a global upper support.  The posterior
mixture of mass (5/8) at (1/5) and (3/8) at (1) attains mean (1/2)
and support value (r); reflection gives the other direction.

The explicit entropic witness uses mutually independent binary components

| component | `C` | `A` | `B1c` | `B2c` | `Eu` | `Ev` | `Ny` | `Nz` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| entropy | (2r) | (1-h) | (r) | (7/4-2h) | (1/2-r) | (r) | (1/2) | (1/2) |

and tuple variables

\[
\begin{aligned}
U&=(C,A,B2c,Eu),&V&=(B1c,Ev),\\
X&=(C,A,B1c,B2c,Eu,Ev),\\
Y&=(C,A,Ny),&Z&=(C,B1c,B2c,Nz),
\end{aligned}
\]

with (W,T) constant.  Since all entropies are affine expressions in (h),
the retained witness can be checked using exact rational coefficient
arithmetic and component-set intersections.

## Reproduction

Run the independent standard-library checker from this contribution directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_exact_witness.py
PYTHONDONTWRITEBYTECODE=1 python3 -O verify_exact_witness.py
```

It verifies exactly, without floating-point arithmetic:

- positivity of all component entropies from
  (3/4<h_2(1/4)<7/8);
- the complete base entropy vector and all structural equalities;
- both zero-valued dependence-balance sides;
- all 65 disjoint-subtuple conditional BEC identities;
- both sharp support rows and both objective branches at
  (2h_2(1/4)-5/4).

It prints:

```text
PASS: exact affine-in-h component audit
PASS: 65 disjoint-subtuple BEC identities
PASS: dependence balance, support rows, and both objective branches
```

The two accepted source submissions are retained byte-for-byte under
`source-artifacts/`; they contain analytic proofs rather than executable
artifacts.  Their immutable SHA-256 hashes are:

```text
a11816b72452187bed84f3d9d32ef6fa2788f444077222fc66854ba2cf9cccc8  upper-dependence-balance/FULL.md
ad7b04c34212cb4dc7debc04fb4c0a37cb4dad1e91dcb14c0000104b8120b779  upper-entropy-nogo/FULL.md
```

For each file, the source-commit blob, official judgment-bundle submission
blob, and retained port blob are identical.

## Provenance, acceptance, and authorship

The read-only source repository is
`/Users/robert/eig/autoresearch/bssc/yukon-bssc-challenge`; its accepted
snapshot is `local-yukon/canonical` at
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c`.

| artifact | source ref and commit | author | judgment commit and fingerprint | Yukon knowledge acceptance |
|---|---|---|---|---|
| finite-block dependence balance | `local-yukon/submissions/upper-dependence-balance`, `e723bc5d85270ff9119e17c07502b6836f91d46e` | Robert (`robert.raynor@gmail.com`) | `2f3e16a6f81ef6d90c003ee5058afc45a20a0602`, `9707a391748afbad90dfbe3d6ac76fe416f132d89778a583e93019172cbc554f` | `c9222de0efdc2a89fbfcaf8d279f94348b8329dc` |
| exact entropy/copy no-go | `local-yukon/submissions/upper-entropy-nogo`, `73f22f13e1a5fa2f6b9c80934cc0d513bae40a30` | Robert (`robert.raynor@gmail.com`) | `43df61ac5aa0858639b1ff5c2a0c81fb172045bc`, `3ce2bbdfbadff26e6d427d563140d84693c5aef1ed376ba601a6181001defa56` | `6374c04275bda4ac538eaba84db03cbf0efba521` |

Both official judgments record `outcome: accepted`, with `accepted: true`,
`advisory: false`, and `mode: official`; their acceptance sequence numbers are
8 and 9.  The second source base is the formed state of the first, and its
theorem explicitly uses the first artifact's dependence balance and fixed-map
structure.  This dependency is why the two artifacts are kept together as one
coherent atomic contribution.

The port preserves Robert's original mathematical authorship.  The exact
checker was added only as an independent reproducibility audit and does not
claim new authorship of the accepted theorems.

## Capacity effect and limitations

There is **no capacity-frontier change**.  The canonical certified bound

```text
C_sum <= 0.369296945969202842443
```

remains unchanged.  The contribution supplies a code-induced necessary
condition and closes one coarse entropy/copy refinement route; it does not
make the value (0.3725562489182657\ldots) a new capacity bound.

- No fixed-alphabet support reduction is proved for the code-induced laws.
- The entropy counterfeit is not produced by the binary BSSC and is excluded
  by complete channel-specific posterior constraints.
- No achievability result, global converse optimization, capacity formula, or
  improvement over the existing upper bound is claimed.
- The result is an unregistered contribution.  It neither updates nor
  completes any research-direction event.
