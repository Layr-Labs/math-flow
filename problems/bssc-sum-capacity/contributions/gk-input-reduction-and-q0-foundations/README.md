# GK input reduction and three-posterior foundations

## Claims

This contribution is an attributed port of three accepted artifacts from the
local Yukon BSSC challenge. The verbatim accepted submissions and their exact
checkers are retained under `source-artifacts/`.

1. In the Gohari--Liu--Nair Theorem 9 equations (19a)--(19p), including
   their two side conditions, every arbitrary finite auxiliary channel
   \(T_{G,K\mid X,Y,Z}\) may be replaced pointwise by
   \[
   T'_{G,K\mid X,Y,Z}=\bar T_{G\mid X}\bar T_{K\mid X},
   \]
   where the two factors are its input-conditioned marginals. Every displayed
   constraint branch and side condition is unchanged. Thus output dependence
   and conditional \(G\)--\(K\) correlation are redundant for this system.

2. At the fair input, represent a finite-output binary-input receiver by its
   posterior measure \(m=\sum_a m_a\delta_{\rho_a}\), whose mean is \(1/2\).
   For a finite posterior grid \(Q\) of size \(N\), containing
   \(\{0,1/2,1\}\), each receiver may be replaced without changing the
   grid-restricted 30-row value \(V_Q\) by one with at most \(N\) outputs.
   If \(Q\) is reflection closed, the replacement preserves reflected pairs.

3. On \(Q_0=\{0,1/2,1\}\), with
   \[
   c=h_2(1/4)-\tfrac12,
   \]
   the unrestricted and reflected receiver optima agree exactly:
   \[
   \inf_{G,K}V_{Q_0}(G,K)=\inf_mV_{Q_0}(m,m^\circ)=c.
   \]

4. The same rung has the pointwise coercive strengthening
   \[
   B(G,K)\ge V_0(g,k)\ge \max\{F(g),F(k)\},\qquad
   F(x)=\frac{2c\max\{c,x\}}{c+x},
   \]
   where \(g=I_G(1/2)\), \(k=I_K(1/2)\), and \(B(G,K)\) is the full
   Theorem 9 sum-rate value. Hence, if \(c\le U<2c\) and
   \(B(G,K)\le U\), then necessarily
   \[
   \frac{2c^2}{U}-c\le g,k\le\frac{Uc}{2c-U}.
   \]

These are structural and finite-grid results. They do not improve either
capacity frontier by themselves.

## Argument

Let \(A=(A_a,A_b,A_c)\) denote the three auxiliary groups. The Theorem 9
factorization gives \(A-X-(Y,Z,G,K)\). Every mutual-information term in the
cited rows and side conditions contains exactly one of \(Y,Z,G,K\) as its
output; none contains \((G,K)\) jointly or conditions one output on another.
For any auxiliary subtuple \(D\),
\[
p(d,x,g)=p_X(x)p_{D\mid X}(d\mid x)
 \sum_{y,z,k}T_{Y,Z\mid X}(y,z\mid x)
 T_{G,K\mid X,Y,Z}(g,k\mid x,y,z),
\]
and the final sum is \(\bar T_{G\mid X}(g\mid x)\). The product replacement
therefore preserves the entire law of \((D,X,G)\); likewise for \(K\), while
the \(Y,Z\) laws are unchanged directly. This proves the first claim in both
directions.

For the receiver reduction, define
\[
\psi(q,\rho)=
2(1-q)(1-\rho)\log_2\frac{1-\rho}{(1-q)(1-\rho)+q\rho}
+2q\rho\log_2\frac{\rho}{(1-q)(1-\rho)+q\rho}.
\]
Then \(I_m(q)=\int\psi(q,\rho)\,dm(\rho)\). Preserving the mean and the
\(N-2\) nonendpoint grid samples is a convex-hull problem in
\(\mathbb R^{N-1}\); Caratheodory's theorem supplies a measure with at most
\(N\) atoms. The identities
\[
I(S;A)=I_A(1/2)-\mathbb E I_A(q_S),\qquad
I(X;A\mid S)=\mathbb E I_A(q_S)
\]
and their conditional versions show that these samples determine every
receiver term in the grid-restricted rows. Reflection covariance
\(I_{m^\circ}(q)=I_m(1-q)\) proves the reflected statement.

On \(Q_0\), choosing \(W=X\) and \(U,V\) constant in every group makes
\((R_1,R_2)=(c,0)\) feasible for all \(G,K\), proving the universal lower
bound. The reflection-invariant revealing-erasure posterior measure
\[
\frac c2\delta_0+(1-c)\delta_{1/2}+\frac c2\delta_1
\]
has the same sampled curve as \(Y,Z\). In the audited sum row `SL(1,U)`, the
cross differences vanish and
\(I(U,W;G)+I(X;G\mid U,W)=I(X;G)=c\), giving the matching upper bound.

Finally, each \(Q_0\)-supported hierarchy block is exactly parameterized by
\[
A,U,V\ge0,\qquad A+U\le1,\quad A+V\le1.
\]
If the receiver midpoint information is \(x\), its seven row terms are
\(Ax,Ux,Vx,(A+U)x,(A+V)x,(1-A-U)x,(1-A-V)x\). The accepted H, L, and X
witness families cover the cases above, below, and straddling \(c\). The
exact checker rebuilds all 30 rows and verifies all row and block-box slacks
as coefficientwise nonnegative polynomials after the stated substitutions.
Skew exchange supplies the complementary branch of \(F\), and exact
inversion of \(F(x)\le U\) gives the midpoint window.

## Reproduction

From this contribution directory, run both accepted standard-library exact
checkers:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 source-artifacts/frontier-global-bridge/verify_q0.py
PYTHONDONTWRITEBYTECODE=1 python3 source-artifacts/frontier-q0-coercive/verify_q0.py
```

Both retained source commits contain the same checker and end with

```text
PASS: exact three-posterior coercive-floor certificate complete
```

The first source submission is symbolic and records no executable command.
Its audit is the displayed factorization, complete single-output term list,
and marginal-law calculation in `source-artifacts/agent-01/FULL.md`.

The original source commands, preserved verbatim in the accepted `FULL.md`
files, use the source-repository prefix `submission/`; the commands above are
the path-adjusted replay commands for this port. No mathematical or executable
content in the source artifacts has been changed.

## Provenance and authorship

The read-only source checkout is `Layr-Labs/bssc-challenge`. Its accepted
local state is branch `local-yukon/canonical` at
`1af4e641fcfd4c76ec382c4e7cd5bed32af15e9c`. All three source submissions
were authored by Robert (`robert.raynor@gmail.com`); this port does not claim
new authorship.

| accepted artifact | source ref | source commit | judgment commit and ID | canonical acceptance commit |
|---|---|---|---|---|
| input-only marginalization | `local-yukon/submissions/agent-01` | `886748411d9e5b4533ca886fffd5d396f42ffec2` | `35666e5a0f715e868581db119102d2c4ea0ad9ed`, `fc56cf03d3802f89de673c56b293728561e1e7eeea38a468ad1186b995e56314` | `ee4e6796f889368e4d9ebbf88b5cdf16113b420d` |
| finite-grid reduction and solved \(Q_0\) rung | `local-yukon/submissions/frontier-global-bridge` | `37f890c29f3bc05796fdf99caa41e04c61f7de03` | `d20e7b6eaaa09cf7139e607f9e6a07fdb133aaa9`, `2d0cf3b6fe7e7d843a1834bdb75adc2afa82a3e08f93928d159333aa25098950` | `3945fd6038b359f9b1ff71eefb1b7f3f80e499d6` |
| midpoint coercivity | `local-yukon/submissions/frontier-q0-coercive` | `8d9516c0c44931b6ccff5927342f38e93fd345a8` | `8db34d65483fdbc9bcdab75dbaccad795d6a0ed6`, `9b8cbe42199241a600929ef1cfc0decc72f432f37ae8514b1581c66f15f9d6e1` | `54a9b21c9870e2c3ef8248b833e5ad7e8fd5b586` |

The files below `source-artifacts/` are byte-for-byte copies from the stated
source commits. The accepted judgment records report `outcome: accepted` for
all three artifacts.

## Limitations

- The marginalization applies only to the displayed Theorem 9 system; it does
  not cover bounds with joint-output or output-conditioned terms.
- The \(N\)-output reduction is for a fixed \(N\)-point posterior grid. It
  gives no continuum cardinality theorem or limit interchange.
- The solved \(Q_0\) rung is a lower approximation to the continuum receiver
  optimization, not a capacity bound.
- The midpoint window is necessary, not sufficient. It gives no off-midpoint
  control, reflected sufficiency, global auxiliary optimum, or capacity
  formula.

## Reference

A. A. Gohari, G. Liu, and C. Nair, *A Two Auxiliary Receiver Outer Bound to
the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast Channel*,
January 2026, Theorem 9 and equations (19a)--(19p).
