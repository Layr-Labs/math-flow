# Fixed-pair continuous certificates and invariant frontier representation

## Claims

This is an attributed port of one cumulative line of four accepted artifacts
from the local Yukon BSSC challenge. The accepted submissions are preserved
verbatim under `source-artifacts/`.

For the half-skew BSSC, the final certificate in this line fixes the reflected
binary auxiliary-receiver pair

\[
G=(0.206961624915382,0.826953249115544),\qquad
K=(0.173046750884456,0.793038375084618)
\]

and proves, for every input prior and every admissible hierarchy in the full
Gohari--Liu--Nair Theorem 9 converse,

\[
\begin{aligned}
C_{\rm sum}\le U\in[&
0.36929694596920284244271335135600317726937686320586339865039784778686683932875798,\\
&0.36929694596920284244271335135600317726937686320586339865039784778686683932875818].
\end{aligned}
\]

Consequently,

\[
\boxed{C_{\rm sum}\le0.369296945969202842443}.
\]

This strictly improves the preceding repaired fixed-pair certificate

\[
C_{\rm sum}\le
0.36929694655551972563539254207215942386102502532943886683678450695288358384488468,
\]

whose group-\(b\) affine inner lines use an intercept of \(10^{-33}\). At
its frozen rounded slope the zero-intercept gap is strictly negative, so exact
zero-backoff feasibility is expressly not claimed.

For every \(0\le\epsilon\le1/3\), the six-row functional used by the final
frontier certificate has an exactly equal skew-invariant nonnegative six-row
representation. At \(\epsilon=0.000173428163029\), its rank-eight quotient
point is

\[
\left(\frac{1-\epsilon}{2},0,\epsilon,0,0,0,0,
\frac{1-\epsilon}{2}\right),
\]

with normalization \(2s_B+s_C+s_D+s_E=1\). This is an exact identity of
posterior-hierarchy functionals, not a numerical near-symmetry.

## Certificate method

This line builds on the input-only auxiliary-receiver reduction and encoded
30-row foundations represented by canonical Math Flow transaction
`d638c346212db3e75f6a53dcebcfd09f55125852`. It nevertheless retains and
replays each certificate's own exact row/tensor audit rather than assuming the
numeric conclusion of that earlier contribution.

The fixed-pair certificates take a nonnegative combination of six scalar
Theorem 9 rows. Exact `Fraction` arithmetic checks that the coefficients of
both rates equal one and expands the complete posterior tensor. For a
binary-input receiver \(A\) with mutual-information curve \(I_A(q)\), the
standard posterior identities include

\[
I(W;A)=I_A(q_0)-\mathbb E I_A(q_W),\qquad
I(U;A\mid W)=\mathbb E I_A(q_W)-\mathbb E I_A(q_U).
\]

Dropping all hierarchy structure except the mass, common-mean, and martingale
constraints is a relaxation. Affine inner majorants and outer lines therefore
give a valid weak-duality upper bound without a minimax exchange or strong
duality assumption.

The checkers certify the affine inequalities on the complete posterior
interval \([0,1]\), not on a sample grid. They combine exact rational
curvature-sign identities, concave endpoint bounds, convex tangent bounds,
reflection, directed endpoint monotonicity where applicable, and fail-closed
adaptive interval subdivision. Arithmetic uses 80-digit directed `Decimal`
intervals; logarithms are expanded outward by one representable value.

In the final certificate, the tensor audit cancels the constant auxiliary-
receiver coefficients and all three outer-line slopes. The remaining prior
bound is a nonnegative multiple of \(I_Y(q)+I_Z(q)\) plus a constant, so it is
concave and reflection symmetric and is globally maximized at \(q=1/2\).

For the invariant representation, the source expands both six-row
combinations into coefficients at root, \(W\), \(U\), and \(V\) posterior
levels. Every nonconstant coefficient agrees groupwise. The only root-level
residuals cancel columnwise because the three groups share the same input
prior. Equal weights on all skew-paired supports establish invariance exactly.

## Reproduction

Run from this contribution directory:

```bash
(cd source-artifacts/agent-02 && PYTHONDONTWRITEBYTECODE=1 python3 certify_th9_dual.py --audit-ambient-context)
(cd source-artifacts/upper-contact-repair && PYTHONDONTWRITEBYTECODE=1 python3 certify_th9_dual.py --audit-ambient-context)
(cd source-artifacts/frontier-bound-state && PYTHONDONTWRITEBYTECODE=1 python3 -B verify.py)
(cd source-artifacts/frontier-continuum-exchange && PYTHONDONTWRITEBYTECODE=1 python3 verify.py)
(cd source-artifacts/frontier-continuum-exchange && PYTHONDONTWRITEBYTECODE=1 python3 -O verify.py)
```

The first two commands end with `ambient_context_audit: passed`. The final
bound checker prints `PASS`, the complete interval above, and the strict
margin below the repaired certificate. The invariant audit ends with
`functional identity: verified for symbolic epsilon` in both ordinary and
optimized Python modes. All checkers use only the Python standard library.

The commands in each accepted `FULL.md` are preserved verbatim and use the
source repository's `submission/` path. The commands above are only the
path-adjusted replay commands for this contribution. No source artifact has
been edited.

## Provenance and authorship

The source repository is `Layr-Labs/bssc-challenge`; the accepted source state
is local branch `local-yukon/canonical` at
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c`.

| accepted artifact | source ref and commit | source author | judgment commit and ID | canonical acceptance commit |
|---|---|---|---|---|
| first continuous fixed-pair certificate | `local-yukon/submissions/agent-02`, `f1c0ed87c4ae99080ddb40db70eed66d0ccb8295` | Robert (`robert.raynor@gmail.com`) | `7d902868f96aef29b91591bd576e48d373547e89`, `944d6e177c8fc809838da5eeb74cc52788d29fe2f73a56ffe6b5b86a55414b8d` | `ba8f0dce05925e17ad29704fb1d40d87ba3c6a6a` |
| repaired near-contact certificate | `local-yukon/submissions/upper-contact-repair`, `b35995472da3d06e67582d95f98e9b176c586b4d` | Red Team D (`redteam-d@invalid`); committed by Robert | `8bcba1c2ba103c0b385f61e96dd51432ee78cf81`, `68a5a52dd97d4a32bae4904c739cdaf9b4b54632ab5531807b3a627b28bdd910` | `a22c4f42a85faf8fac63e9f31e8c05f908dd9e64` |
| improved frontier certificate | `local-yukon/submissions/frontier-bound-state`, `51a844c7ca1b89cecdc37cbed5f045b64c21f545` | Robert (`robert.raynor@gmail.com`) | `479eaa429ffda1159c872e1a4659feea5c4a1949`, `4db7695e0b1b71592409cc14cfd689df3c9438e48b17102b46bdd02d86fb2e30` | `8066727e1a20d1b75cf93e5c5123c9f892ded2d7` |
| invariant representation of the frontier functional | `local-yukon/submissions/frontier-continuum-exchange`, `249466a460e0a2a02fa50f5f23bce5c7b13de958` | Robert (`robert.raynor@gmail.com`) | `1d764be1ffa04e171c89ec22e32818b37d2af8fa`, `6cd87c481f1d32a0bef96000b92c3aae6214d2bcb23d13f827a724d79a11287d` | `0f66bf52026b0d5f76f90bcd6be1c8a184078db9` |

The retained files are byte-for-byte copies from the source commits listed in
the table. Their judgment bundles all record `outcome: accepted`. This port
claims no new authorship.

## Scope and limitations

- These are valid fixed-pair full-Theorem-9 converse certificates. They do
  not prove that either receiver pair or dual face is locally or globally
  optimal.
- They do not prove binary auxiliary cardinality, reflected-pair sufficiency,
  a capacity formula, or matching achievability.
- The reported value near \(0.369296340638082\) is not certified here.
- The exact invariant representation is proved only for this frontier
  functional. It does not show that every globally optimal dual functional
  can be chosen invariant.
- The frozen-surrogate floors and exclusion regions derived elsewhere for the
  earlier weighting do not automatically transfer to the improved frontier
  weighting.
- `STATE_TRANSITION_FIXTURE.md` is retained because it was part of the
  accepted frontier submission, but its source explicitly labels it a
  non-normative candidate knowledge-state fixture; the mathematical evidence
  is `FULL.md` and `verify.py`.

## Reference

A. A. Gohari, G. Liu, and C. Nair, *A Two Auxiliary Receiver Outer Bound to
the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast Channel*,
January 2026, Theorem 9 and equations (19a)--(19p).
