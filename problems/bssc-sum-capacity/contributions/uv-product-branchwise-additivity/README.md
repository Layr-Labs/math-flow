# Exact UV product and branchwise additivity

## Claim and scope

This contribution independently ports and rechecks the two accepted Yukon
artifacts `upper-uv-additivity` and `frontier-uv-branchwise`.  They form one
dependency-ordered theorem chain for the two separately relaxed UV sum-rate
rows.

For a finite-alphabet discrete memoryless broadcast channel \(W\), write

\[
t_W(p)=I_p(X;Y)-I_p(X;Z)
\]

and let \(\mathfrak C\) denote the upper concave envelope on the input
simplex.  Define

\[
A_W(p)=I_p(X;Y)+\mathfrak C[-t_W](p),
\qquad
D_W(p)=I_p(X;Z)+\mathfrak C[t_W](p),
\]

\[
B_{\rm avg}(W)=\sup_p\frac{A_W(p)+D_W(p)}2,
\qquad
B_{\rm br}(W)=\sup_p\min\{A_W(p),D_W(p)\}.
\]

The checked claims are:

1. For arbitrary finite-alphabet DMBCs,
   \[
   B_{\rm avg}(W_1\times W_2)
   =B_{\rm avg}(W_1)+B_{\rm avg}(W_2).
   \]
   The product-channel prior may be correlated and the envelope auxiliary may
   be joint across factors.
2. If an involutive input relabeling exchanges the two receivers, then
   \[
   B_{\rm br}(W)=B_{\rm avg}(W),
   \]
   and the optimum may be restricted to invariant input laws.
3. Finite products preserve this receiver-skew symmetry, so both scalar
   functionals are exactly additive on arbitrary finite products of such
   channels.
4. For the half-skew BSSC \(P\), the unique invariant binary prior is the fair
   prior.  Combining the theorem with the sharp BSSC posterior support already
   represented by canonical transaction
   `c70e1829a7c6a2a8cb8cfc2383f8abf825ac5ea6` gives
   \[
   B_{\rm br}(P^{\times n})=B_{\rm avg}(P^{\times n})
   =n\left(2h_2(1/4)-\frac54\right)
   \]
   for every finite \(n\ge1\).  Numerically, the normalized value is
   \(0.3725562489182657\ldots\) bits per channel use.

The last value is a valid but non-frontier UV converse.  It is weaker than the
current certified full-Theorem-9 capacity upper bound
\(0.369296945969202842443\), so this contribution does not move either endpoint
of the governed capacity interval.

This is an ordinary unregistered contribution.  The UV program lies outside
the registered `yukon-auxiliary-converse-port` scope, and this contribution
does not claim to advance or complete that direction.

## Argument

For any finite auxiliary

\[
A-(X_1,X_2)-(Y_1,Z_1,Y_2,Z_2)
\]

on a product DMBC, the crucial exact identity is

\[
\begin{aligned}
&I(X_1X_2;Y_1Y_2\mid A)-I(X_1X_2;Z_1Z_2\mid A)\\
&=I(X_1;Y_1\mid A,Z_2)-I(X_1;Z_1\mid A,Z_2)\\
&\quad+I(X_2;Y_2\mid A,Y_1)-I(X_2;Z_2\mid A,Y_1).
\end{aligned}
\]

The two chain-rule correction terms are both
\(I(Y_1;Z_2\mid A)\) and cancel.  The conditioned variables
\((A,Z_2)\) and \((A,Y_1)\) remain valid one-factor auxiliaries.  Applying the
one-factor envelopes and their concavity gives

\[
\mathfrak C[\pm t_{12}](p_{12})
\le
\mathfrak C[\pm t_1](p_1)+\mathfrak C[\pm t_2](p_2)
\]

even for correlated \(p_{12}\).  Mutual-information subadditivity proves the
product upper bound.  Product priors and independent near-optimal posterior
decompositions prove the reverse inequality.

For a receiver-skew involution \(S\), posterior decompositions are carried
bijectively to posterior decompositions and \(t(Sp)=-t(p)\).  Hence

\[
A_W(Sp)=D_W(p),\qquad D_W(Sp)=A_W(p).
\]

Both rows are concave.  At \(\bar p=(p+Sp)/2\), each row is therefore at least
the average of the two rows at \(p\).  This gives
\(B_{\rm br}\ge B_{\rm avg}\); the pointwise inequality
\(\min(a,d)\le(a+d)/2\) gives the reverse direction.

For the BSSC, put \(h=h_2(1/4)\), \(c=h-1/2\), and \(r=h-3/4\).  The sharp
canonical support from transaction `c70e182...` and its reflection give
\(t(q)\le2rq\).  Thus every fair-prior posterior decomposition has mean
\(1/2\) and average \(t\) at most \(r\).  Equality is attained by the source
mixture with masses \(5/8\) at \(q=4/5\) and \(3/8\) at \(q=0\), since
\(t(4/5)=8r/5\).  Therefore the relevant envelope value is exactly \(r\), and
the fair-prior UV value is

\[
c+r=2h_2(1/4)-\frac54.
\]

## Immutable Yukon provenance

All source reads were made from the dirty-worktree-independent Git objects of
`/Users/robert/eig/autoresearch/bssc/yukon-bssc-challenge`.  The accepted
formed source snapshot is `local-yukon/canonical` commit
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c`.

### Averaged functional

- Original source commit: `1e41cfadf20ec6d1e149547d10b074d882a6cb79`
- Original author: Robert `<robert.raynor@gmail.com>`
- Source subject: `Prove exact UV product additivity`
- Accepted judgment ID:
  `71f4dc08876d2e6aeee3b569f30e2142fdaf845d0d5cd4df5ef69168d19cda80`
- Immutable judgment commit:
  `fdd2dc2137e1e0ca5dd38acd1fdc89f5c09f056f`
- Formed Yukon knowledge commit:
  `31c4c4ef5e72a1099863905267a681efe2d26a40`
- `FULL.md` Git blob: `06834d7020429bcae39e5f321787b6a4f191e381`
- `verify_uv_factorization.py` Git blob:
  `93efd576e1652ca77ee78a89db095f19d3759f55`

The judgment verdict was `ACCEPT`.  It specifically accepted the correlated
input chain-rule identity, both envelope inequalities, exact arbitrary-product
additivity, and the all-blocklength structural consequence, while excluding
the complete UV region, branchwise minimum, and the GK/Theorem-9 systems.

### Branchwise functional

- Original source commit: `7f51930dd39a89c0a0a4e78d8630f39da8e6c87f`
- Original author: Robert `<robert.raynor@gmail.com>`
- Source subject: `Prove branchwise UV additivity under skew symmetry`
- Accepted judgment ID:
  `d2251d88c98360c9b6db0a22daedc778c667bb66c2e70999cff67a1ec72909e7`
- Immutable judgment commit:
  `f7046f55f817c02f80d086b34b18fb5e1038e3c5`
- Formed Yukon knowledge commit:
  `ccee6b9529621884c014db5a81dc5c2f6a67c6f0`
- `FULL.md` Git blob: `e020e5c85c3e101baddda12fba5dd906b2a72ac9`

Its judgment verdict was also `ACCEPT`.  It accepted envelope covariance,
symmetrization, equality of the two scalar optima, closure of skew symmetry
under products, and the inherited all-blocklength BSSC result.

The three copied source files in `source-artifacts/` are byte-identical to
their original source-commit blobs.  Porting preserves the original
authorship; it is not a claim of new authorship for those results.

## Reproduction

From the repository root, run:

```text
python3 problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/verify_uv_factorization.py
python3 problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/verify_uv_hostile_cases.py
```

The first command is the original dependency-free, deterministic Yukon audit.
It checks random strictly positive finite product channels, correlated input
laws, the coefficient-one and general-coefficient chain identities,
mutual-information subadditivity, product posterior mixtures, and the BSSC
contact value.  The second command independently adds deterministic channels,
zero-probability rows, perfectly correlated and degenerate inputs, exact BSSC
skew-matrix checks, and a 90-digit Decimal contact evaluation.

Byte identity can be checked with:

```text
git hash-object problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/FULL.md
git hash-object problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/upper-uv-additivity/verify_uv_factorization.py
git hash-object problems/bssc-sum-capacity/contributions/uv-product-branchwise-additivity/source-artifacts/frontier-uv-branchwise/FULL.md
```

The expected hashes, in order, are `06834d7020429bcae39e5f321787b6a4f191e381`,
`93efd576e1652ca77ee78a89db095f19d3759f55`, and
`e020e5c85c3e101baddda12fba5dd906b2a72ac9`.

## Limitations

- The scalar rows optimize their envelope auxiliaries separately.  The theorem
  does not establish tensorization of the complete UV rate region or a common
  joint-\((U,V)\) optimization.
- Branchwise equality is proved only under receiver-skew symmetry; no claim is
  made for nonsymmetric channels or other weighted scalarizations.
- Nothing here tensorizes the simplified GK functional or the full
  Gohari--Liu--Nair Theorem-9 system.
- The executable checks are corroboration.  The universal finite-alphabet
  theorem rests on the displayed analytic identities and concavity argument.
- The original averaged-functional artifact labels its sampled BSSC decimals
  as non-certified.  The exact BSSC specialization here instead uses the sharp
  posterior support already accepted and represented under canonical Math Flow
  transaction `c70e182...`.
- This contribution changes no capacity frontier and supplies no achievable
  coding improvement.
