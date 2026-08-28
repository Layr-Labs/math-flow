# Paired-output KL curvature sharpens two-letter BSSC covariance pruning

## Claim and scope

Let \(P\) be the governed half-skew BSSC, let
\(S=(X_1,X_2)\) be any input to \(P^{\otimes2}\), and put

\[
q_i=\Pr[X_i=1],\qquad
c_{\rm in}=P_S(11)-q_1q_2=\operatorname{Cov}(X_1,X_2).
\tag{1}
\]

For the two receiver output pairs, define

\[
C_{\rm out}:=I(Y_1;Y_2)+I(Z_1;Z_2).
\tag{2}
\]

This contribution proves the unconditional channel-specific curvature bound

\[
\boxed{
C_{\rm out}\geq\frac{31}{20\ln2}\,c_{\rm in}^2.}
\tag{3}
\]

Canonical transaction
`9bb22afe5abd3e1d9f419c1717bd61bb33a958ff` proves that every finite
two-letter Marton law whose unnormalized value \(M\) exceeds
\(T=2L_{\rm RTD}\) has \(C_{\rm out}<7/160\). Combining that result with
(3) gives the sharpened necessary condition

\[
\boxed{
M>T\quad\Longrightarrow\quad
|c_{\rm in}|<\sqrt{\frac{7\ln2}{248}}<\frac7{50}=0.14.}
\tag{4}
\]

This is stronger than the preliminary bounded-marginal estimate
\(|c_{\rm in}|<13/80\). It is a necessary condition only: it neither
constructs a Marton gain nor rules one out.

## 1. The bounded-marginal route

The canonical prerequisite also proves \(q_i\in(3/8,5/8)\) for a gain. This
already improves ordinary Pinsker. For one receiver \(R\), fix its two output
marginals and parametrize its binary joint table by its covariance \(d\):

\[
p_{11}(d)=r_1r_2+d,\quad
p_{10}(d)=r_1(1-r_2)-d,\quad
p_{01}(d)=(1-r_1)r_2-d,\quad
p_{00}(d)=(1-r_1)(1-r_2)+d.
\tag{5}
\]

In bits, direct differentiation gives

\[
\frac{d^2}{d d^2}
D_2(P_d\|P_0)
=\frac1{\ln2}\sum_{a,b\in\{0,1\}}\frac1{p_{ab}(d)}.
\tag{6}
\]

Partitioning the four cells by the first output and applying Cauchy gives

\[
\sum_{a,b}\frac1{p_{ab}(d)}
\geq4\left(\frac1{r_1}+\frac1{1-r_1}\right)
=\frac4{r_1(1-r_1)}.
\tag{7}
\]

For the half-skew BSSC and \(q_1\in(3/8,5/8)\), the \(Y_1\) output-one
marginal lies in \((11/16,13/16)\), while the \(Z_1\) output-one marginal
lies in \((3/16,5/16)\). In either case
\(r_1(1-r_1)\leq55/256\). Both receiver output covariances equal
\(d=c_{\rm in}/4\), so integrating (6)--(7) twice from independence gives

\[
C_{\rm out}\geq\frac{64}{55\ln2}\,c_{\rm in}^2.
\tag{8}
\]

Together with \(C_{\rm out}<7/160\), this yields

\[
|c_{\rm in}|<\sqrt{\frac{77\ln2}{2048}}<\frac{13}{80}.
\tag{9}
\]

The next argument improves (8) by using both receiver tables jointly. It no
longer needs the marginal window.

## 2. A paired eight-cell reciprocal lemma

At an arbitrary point along the fixed-marginal covariance segment, write

\[
y_{ab}=P(Y_1=a,Y_2=b),\qquad
z_{ab}=P(Z_1=a,Z_2=b).
\]

The BSSC marginal laws give, for each coordinate \(i\),

\[
P(Y_i=0)+P(Z_i=1)=\frac{1-q_i}{2}+\frac{q_i}{2}=\frac12.
\tag{10}
\]

In the \(Y\) table mark the event \(\{Y_i=0\}\), and in the \(Z\) table
mark \(\{Z_i=1\}\). Sum the two tables' masses separately for each of the
four two-coordinate membership vectors, and put

\[
\begin{array}{c|c}
\text{membership class}&\text{class total}\\ \hline
(1,1)&x:=y_{00}+z_{11}\\
(1,0)&y_{01}+z_{10}\\
(0,1)&y_{10}+z_{01}\\
(0,0)&y_{11}+z_{00}.
\end{array}
\]

The two identities (10) and the total mass two of the disjoint union of the
two receiver tables force the four class totals, in the relative interior, to
be

\[
x,\qquad \frac12-x,\qquad \frac12-x,\qquad 1+x,
\quad 0<x<\frac12.
\tag{11}
\]

For two positive numbers of sum \(s\), Cauchy gives
\(1/u+1/v\geq4/s\). Applying this separately to the two cells in each class
proves

\[
\begin{aligned}
R&:=\sum_{a,b}\left(\frac1{y_{ab}}+\frac1{z_{ab}}\right)\\
&\geq4\left[
\frac1x+\frac2{1/2-x}+\frac1{1+x}
\right].
\end{aligned}
\tag{12}
\]

The right side is strictly greater than \(248/5\). To see this without a
numerical minimization, set

\[
p(x)=124x^3+62x^2-42x+5.
\]

Indeed, direct expansion gives

\[
5x(1/2-x)(1+x)
\left\{
4\left[\frac1x+\frac2{1/2-x}+\frac1{1+x}\right]-\frac{248}{5}
\right\}
=2p(x).
\]

The factor on the left is positive for \(0<x<1/2\), so the asserted
comparison reduces to \(p(x)>0\). Now

\[
p'(x)=372x^2+124x-42,\qquad p''(x)=744x+124>0.
\]

Moreover,

\[
p'(1/5)=-\frac{58}{25}<0,qquad
p'(21/100)=\frac{1113}{2500}>0,
\]

so the unique minimum lies in \((1/5,21/100)\). Writing
\(x=1/5+t\), \(0\leq t\leq1/100\), gives the exact expansion

\[
p(x)=124t^3+\frac{682}{5}t^2-\frac{58}{25}t+\frac9{125}
\geq\frac{61}{1250}>0.
\tag{13}
\]

This proves the uniform paired-table lemma

\[
\boxed{R>\frac{248}{5}.}
\tag{14}
\]

If a covariance segment meets a zero cell, the same conclusion follows by
approaching from its relative interior; the relevant divergence is continuous
and the reciprocal curvature diverges at the zero boundary. If an output
marginal is degenerate, then one input coordinate is deterministic,
\(c_{\rm in}=0\), and (3) is immediate.

## 3. From curvature to covariance pruning

For the BSSC, the conditional output-one means are

\[
\Pr[Y=1\mid X]=\frac12+\frac X2,
\qquad
\Pr[Z=1\mid X]=\frac X2.
\]

Memorylessness therefore gives, for both receivers,

\[
\operatorname{Cov}(Y_1,Y_2)
=\operatorname{Cov}(Z_1,Z_2)=\frac14c_{\rm in}.
\tag{15}
\]

Let \(d=c_{\rm in}/4\) and let

\[
\Phi(d)=I(Y_1;Y_2)+I(Z_1;Z_2)
\]

along the fixed-output-marginal segment from independence to the actual two
tables. Equations (6) and (14) give pointwise

\[
\Phi''(d)>\frac{248}{5\ln2}.
\tag{16}
\]

Because \(\Phi(0)=\Phi'(0)=0\), integrating (16) twice gives

\[
C_{\rm out}=\Phi(d)
\geq\frac{124}{5\ln2}d^2
=\frac{31}{20\ln2}c_{\rm in}^2,
\]

which is (3). The non-strict inequality is retained to cover all boundary
cases by continuity.

Finally, the prerequisite's \(C_{\rm out}<7/160\) gives

\[
c_{\rm in}^2<\frac{7\ln2}{248}.
\]

The included directed checker certifies

\[
\frac{7\ln2}{248}<\left(\frac7{50}\right)^2,
\tag{17}
\]

and hence proves (4).

## Directed verification

Run from this contribution directory using only Python's standard library:

```text
python3 -I -B verify.py
```

The checker performs no writes and no network access. It verifies the exact
claim metadata and direct dependency, the rational identities behind
(11)--(14), the monotonicity/minimum bracket for \(p\), the curvature
rescaling \(248/5\mapsto31/20\), and directed logarithmic comparisons proving
both (9) and (17). The information-theoretic reduction and the
twice-integrated curvature argument remain the human-checkable proof.

## Dependency, limitations, and attribution

- The curvature theorem (3) is unconditional for the half-skew BSSC product
  marginals. The gain corollary (4) depends directly on canonical transaction
  `9bb22afe5abd3e1d9f419c1717bd61bb33a958ff` only for
  \(C_{\rm out}<7/160\). Section 1 additionally uses that transaction's
  \(q_i\in(3/8,5/8)\) solely to document the weaker \(13/80\) route.
- The foundation and full-support transactions used by the prerequisite are
  transitive context, not direct mathematical premises of this contribution.
- No claim here constructs a Marton witness, proves no gain, tensorizes the
  Marton functional, or gives a capacity converse.
- The two receiver tables in the curvature proof are marginal tables; no
  particular within-use coupling of \(Y\) and \(Z\) is assumed.
- No external mathematical source is used. The proof is a new elementary
  corollary in the non-exclusive `bssc-multiletter-marton-frontier` direction
  registered by transaction
  `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.
