# Full super-input support is necessary for a two-letter Marton gain

## Claim and scope

Let \(P\) be the half-skew BSSC in the governed problem, and let
\(P^{\otimes 2}\) have super-input
\(S=(X_1,X_2)\in\{00,01,10,11\}\). For a finite Marton law write

\[
\begin{aligned}
M={}&\min\{I(W;Y^2),I(W;Z^2)\}
 +I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),\\
 &(W,U,V)-S-(Y^2,Z^2).
\end{aligned}
\]

This contribution proves the support-pruning theorem

\[
 \boxed{|\operatorname{supp}P_S|\leq3\quad\Longrightarrow\quad
 M<0.695\ \text{bits}.}
 \tag{1}
\]

For a fully internal comparison, use a fair one-letter
randomized-time-division schedule with reflected conditional input priors
\(q=\Pr[X=1]=1/6\) and \(1-q=5/6\), directing the first state to \(Z\)
and the second to \(Y\). If \(J(q)=h_2(q/2)-q\), both common mutual informations
are

\[
J(1/2)-\frac{J(1/6)+J(5/6)}2,
\]

and the private term is \(J(1/6)\). Two independent copies therefore have
the exact unnormalized value

\[
B_{1/6}:=2h_2(1/4)+h_2(1/12)-h_2(5/12)-\frac13
>0.7231.
\tag{2}
\]

The included directed checker certifies the last inequality. Thus the
optimal repeated one-letter RTD benchmark is at least \(B_{1/6}\), and every
two-letter Marton witness that strictly improves that benchmark must give
**positive probability to all four** super-input symbols. In fact the proof
gives the quantitative interiority condition

\[
 P_S(00),P_S(11)>\frac1{180},\qquad
 P_S(01),P_S(10)>\frac1{325}.
 \tag{Q}
\]

This strengthens the canonical two-symbol pruning result, but does not depend
on it. The proof is self-contained: it does not assume the binary-input
Marton theorem, product additivity of a relaxed UV functional, the exact
governed RTD decimal, or any theorem from the 2026 multiletter counterexample
papers. It derives the two UV-style rows needed below directly from the
Marton expression, proves the one-letter BSSC support lines by calculus, and
proves the required two-factor identity by the chain rule.

This supplies the next structural-pruning step in the non-exclusive
`bssc-multiletter-marton-frontier` direction registered by canonical
transaction `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.

## 1. A support-sensitive universal bound

Put

\[
h=h_2(1/4),\qquad r=h-\frac34>0,
\]

and let \(q=\Pr[X=1]\) for a single use. The two receiver mutual
informations are

\[
 I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
 I_Z(q)=h_2(q/2)-q.
 \tag{3}
\]

Define \(g(q)=I_Z(q)-I_Y(q)\). On the open unit interval,

\[
 g''(q)=\frac{2q-1}
 {\ln(2)q(1-q)(1+q)(2-q)}.
\]

Direct substitution gives

\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r.
\]

Thus the tangent at \(1/5\) is \(2r(1-q)\). On \([0,1/2]\), concavity
puts \(g\) below this tangent. On \([1/2,1]\), convexity and
\(g(1/2)=g(1)=0\) give \(g(q)\leq0\leq2r(1-q)\). Receiver reflection,
\(g(1-q)=-g(q)\), gives the second support line:

\[
 g(q)\leq2r(1-q),\qquad -g(q)\leq2rq
 \quad(0\leq q\leq1).
 \tag{4}
\]

Fix any one-use coupling of the two governed receiver marginals and take its
memoryless product; every quantity below depends only on those marginals.
Let \(C-S-(Y^2,Z^2)\) be any finite auxiliary and let
\(q_i=\Pr[X_i=1]\). The product-channel chain identity is

\[
\begin{aligned}
&I(S;Y^2\mid C)-I(S;Z^2\mid C)\\
&=I(X_1;Y_1\mid C,Z_2)-I(X_1;Z_1\mid C,Z_2)\\
&\quad+I(X_2;Y_2\mid C,Y_1)-I(X_2;Z_2\mid C,Y_1).
\end{aligned}
\tag{5}
\]

For completeness, the two expansions whose difference gives (5) are

\[
\begin{aligned}
I(S;Y^2\mid C)
 &=I(X_1;Y_1\mid C,Z_2)+I(X_2;Y_2\mid C,Y_1)
   +I(Y_1;Z_2\mid C),\\
I(S;Z^2\mid C)
 &=I(X_1;Z_1\mid C,Z_2)+I(X_2;Z_2\mid C,Y_1)
   +I(Y_1;Z_2\mid C).
\end{aligned}
\]

Given each value of the conditioning variables in (5), the remaining
coordinate is still governed by the one-letter BSSC. Applying the second
inequality in (4) pointwise and averaging the posterior input probabilities
yields

\[
 I(S;Y^2\mid C)-I(S;Z^2\mid C)\leq2r(q_1+q_2).
 \tag{6}
\]

Exchanging \(Y\) and \(Z\) in (5), and applying the first inequality in
(4), similarly gives

\[
 I(S;Z^2\mid C)-I(S;Y^2\mid C)
 \leq2r(2-q_1-q_2).
 \tag{7}
\]

We next reduce the Marton expression itself. Take
\(A=(W,U)\) and \(B=(W,V)\). The Csiszar identity and data processing give

\[
\begin{aligned}
M
&\leq I(W,U;Y^2)+I(V;Z^2\mid W)-I(U;V\mid W)\\
&=I(A;Y^2)+I(V;Z^2\mid W,U)-I(U;V\mid W,Z^2)\\
&\leq I(A;Y^2)+I(S;Z^2\mid A),
\end{aligned}
\tag{8}
\]

and, symmetrically,

\[
M\leq I(B;Z^2)+I(S;Y^2\mid B).
\tag{9}
\]

Because \(A-S-(Y^2,Z^2)\) and \(B-S-(Y^2,Z^2)\), equations (7)--(9)
imply

\[
\begin{aligned}
M&\leq I(S;Y^2)+2r(2-q_1-q_2),\\
M&\leq I(S;Z^2)+2r(q_1+q_2).
\end{aligned}
\]

Averaging these two valid upper bounds proves the key inequality

\[
\boxed{
M\leq G(P_S)+2r,\qquad
G(P_S):=\frac{I(S;Y^2)+I(S;Z^2)}2.}
\tag{10}
\]

Unlike the unrestricted additive UV constant, the ordinary mutual-information
term \(G(P_S)\) retains the correlation of \((X_1,X_2)\). A missing
super-input symbol forces enough correlation to make (10) decisive.

## 2. The four faces form two symmetry orbits

Two exact channel symmetries will be used:

- coordinate transposition \(\tau(x_1x_2)=x_2x_1\), with the same
  transposition of both receiver outputs; and
- receiver-skew reflection \(\kappa(x_1x_2)=\bar x_1\bar x_2\), which swaps
  the two receivers after bit-complementing their outputs.

The functional \(G\) is concave in the input law and invariant under both
transformations (under \(\kappa\), its two summands are exchanged). The four
three-symbol faces therefore split into

\[
\begin{array}{c|c|c}
\text{orbit}&\text{representative support}&\text{other support}\\ \hline
\mathcal F_{\rm end}&\{01,10,11\}\ (00\text{ missing})
  &\{00,01,10\}\ (11\text{ missing})\\
\mathcal F_{\rm mixed}&\{00,10,11\}\ (01\text{ missing})
  &\{00,01,11\}\ (10\text{ missing}).
\end{array}
\tag{11}
\]

Every support of size at most three lies in at least one of these faces.

## 3. Exact maximum on the missing-\(00\) orbit

On \(\{01,10,11\}\), coordinate transposition exchanges \(01\) and
\(10\). Concavity and invariance show that symmetrizing those two masses
cannot decrease \(G\). Write

\[
P(01)=P(10)=s,\qquad P(11)=1-2s,\qquad 0\leq s\leq\frac12.
\]

The \(Y^2\) output law is \((s/2,s/2,1-s)\) on its three nonzero symbols,
and the \(Z^2\) output law is

\[
\left(\frac{1+2s}{4},\frac14,\frac14,
      \frac{1-2s}{4}\right).
\]

The corresponding row-entropy averages are \(2s\) and \(2-2s\). Hence

\[
\begin{aligned}
I(S;Y^2)&=h_2(s)-s,\\
I(S;Z^2)&=H_4\!\left(\frac{1+2s}{4},\frac14,\frac14,
                     \frac{1-2s}{4}\right)-2+2s.
\end{aligned}
\tag{12}
\]

Differentiation gives

\[
\begin{aligned}
G'(s)&=\frac12\left[
 \log_2\frac{1-s}{s}
 +\frac12\log_2\frac{1-2s}{1+2s}+1\right],\\
G''(s)&=-\frac1{2\ln2}\left[
 \frac1{s(1-s)}+\frac2{1-4s^2}\right]<0.
\end{aligned}
\tag{13}
\]

At \(s=2/5\), the derivative vanishes exactly. Substitution into (12)
therefore gives the global maximum

\[
\max_{\mathcal F_{\rm end}}G
=\frac34\log_2\frac53
=0.5527241956246547\ldots.
\tag{14}
\]

Together with (10), this orbit satisfies

\[
M\leq\frac34\log_2\frac53+2r
=0.6752804445429204\ldots<0.676.
\tag{15}
\]

## 4. A rational tangent certificate on the missing-\(01\) orbit

On \(\{00,10,11\}\), the composite \(\kappa\tau\) exchanges \(00\) and
\(11\), fixes \(10\), and exchanges the receiver terms in \(G\).
Symmetrization therefore reduces the maximization to

\[
P(00)=P(11)=\frac{1-s}{2},\qquad P(10)=s,\qquad0\leq s\leq1.
\]

The two receiver mutual informations are then equal. The \(Y^2\) output law
and its average conditional entropy are

\[
\left(\frac{1-s}{8},\frac{1-s}{8},
      \frac{1+3s}{8},\frac{5-s}{8}\right),\qquad
H(Y^2\mid S)=1.
\]

Consequently

\[
G(s)=H_4\!\left(\frac{1-s}{8},\frac{1-s}{8},
                 \frac{1+3s}{8},\frac{5-s}{8}\right)-1,
\tag{16}
\]

with

\[
\begin{aligned}
G'(s)&=\frac18\log_2
 \frac{(1-s)^2(5-s)}{(1+3s)^3},\\
G''(s)&=-\frac1{8\ln2}\left[
 \frac2{1-s}+\frac1{5-s}+\frac9{1+3s}\right]<0.
\end{aligned}
\tag{17}
\]

Use the exact rational point \(s_0=1/6\). Since

\[
G'(s_0)=\frac18\log_2\frac{725}{729}<0,
\]

global concavity and the tangent inequality give, for all \(s\in[0,1]\),

\[
\begin{aligned}
G(s)
&\leq G(s_0)+G'(s_0)(s-s_0)\\
&\leq G(s_0)-\frac16G'(s_0)\\
&=H_4(5/48,5/48,9/48,29/48)-1
  -\frac1{48}\log_2\frac{725}{729}\\
&=0.5720017298642940\ldots<0.573.
\end{aligned}
\tag{18}
\]

Equations (10) and (18) now give the worst of the two face-orbit bounds:

\[
M<0.5720017298642941+0.1225562489182657
 <0.695<B_{1/6}.
\tag{19}
\]

This proves (1), and hence the full-support necessity claim.

## 5. Quantitative distance from every face

The same argument gives more than positivity. Fix any symbol \(x\), put
\(m=P_S(x)<1\), and let \(Q\) be the normalized law of \(S\) conditional on
\(S\ne x\). Introduce the indicator \(J=\mathbf 1\{S=x\}\). For either
receiver output \(O\in\{Y^2,Z^2\}\),

\[
\begin{aligned}
I(S;O)&=I(J;O)+I(S;O\mid J)\\
&\leq h_2(m)+(1-m)I_Q(S;O).
\end{aligned}
\]

After averaging the receivers,

\[
G(P_S)\leq h_2(m)+(1-m)G(Q).
\tag{20}
\]

If \(x\in\{00,11\}\), equation (14) gives
\(G(Q)\leq C_{\rm end}:=\tfrac34\log_2(5/3)\). If
\(x\in\{01,10\}\), equation (18) gives
\(G(Q)\leq C_{\rm mixed}\), where

\[
C_{\rm mixed}:=
H_4(5/48,5/48,9/48,29/48)-1
-\frac1{48}\log_2\frac{725}{729}.
\]

For either constant \(C<1\), the function
\(\phi_C(m)=h_2(m)+(1-m)C\) has derivative

\[
\phi_C'(m)=\log_2\frac{1-m}{m}-C.
\]

It is therefore increasing throughout each small interval used below. The
directed checker certifies

\[
\begin{aligned}
\phi_{C_{\rm end}}(1/180)+2r
 &<0.721824<B_{1/6},\\
\phi_{C_{\rm mixed}}(1/325)+2r
 &<0.722905<B_{1/6}.
\end{aligned}
\tag{21}
\]

Combining (10), (20), monotonicity, and (21) proves the mass floors (Q) for
every law that improves on the optimal repeated one-letter RTD benchmark:
such a law must in particular improve on the explicit value \(B_{1/6}\).

## Reproduction

Run from this contribution directory using only the Python standard library:

```text
python3 -I -B verify.py
```

The checker constructs the product BSSC transition matrices in exact
`Fraction` arithmetic, verifies the two face orbits and both input/output
symmetries, and checks the affine output laws used in (12) and (16). It then
uses 80-digit outward-expanded `Decimal` intervals to check the exact
missing-\(00\) value, the sign and endpoint use of the rational tangent in
(18), both face bounds, the explicit rational-schedule RTD witness, the
quantitative mass floors, and all strict separations. These computations are
mechanical corroboration; the universal Marton-to-UV reduction, chain
identity, calculus support lines, RTD construction, and concavity arguments
above are the proof.

## Limitations and provenance

- This is a theorem about the unnormalized two-letter Marton functional. It
  is not a converse for unrestricted block codes and does not change the
  governed capacity interval.
- It gives a necessary, not sufficient, condition for a two-letter Marton
  gain. It neither constructs a full-support gain nor rules one out.
- The bound \(0.695\) and the rational mass floors are deliberately coarse.
  The exact/tangent orbit bounds are recorded to make the strict comparisons
  robust, not to claim the exact Marton value of either ternary subchannel.
- The 2026 ternary-input counterexamples motivate examining three-symbol
  support, but no result or numerical value from those papers is used here.

The proof and checker were prepared by an OpenAI Codex solver agent at Robert
Raynor's request.
