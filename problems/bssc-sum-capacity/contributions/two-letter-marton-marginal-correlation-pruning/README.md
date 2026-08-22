# Marginal balance and output decorrelation are necessary for a two-letter Marton gain

## Claim and scope

Let \(P\) be the governed half-skew BSSC, let
\(S=(X_1,X_2)\) be the input of \(P^{\otimes2}\), and consider any finite
Marton law

\[
 (W,U,V)-S-(Y^2,Z^2).
\]

Write its unnormalized two-use Marton sum value as

\[
\begin{aligned}
M={}&\min\{I(W;Y^2),I(W;Z^2)\}
 +I(U;Y^2\mid W)+I(V;Z^2\mid W)-I(U;V\mid W),
\end{aligned}
\tag{1}
\]

put \(q_i=\Pr[X_i=1]\), \(Q=q_1+q_2\), and define the total
within-receiver output correlation

\[
C_{\rm out}:=I(Y_1;Y_2)+I(Z_1;Z_2).
\tag{2}
\]

Also put

\[
c_{\rm in}:=P_S(11)-q_1q_2=\operatorname{Cov}(X_1,X_2).
\tag{2a}
\]

Let \(L_{\rm RTD}\) be the exact one-letter randomized-time-division value
and \(T=2L_{\rm RTD}\). This contribution proves the necessary conditions

\[
\boxed{
M>T\quad\Longrightarrow\quad
q_1,q_2\in\left(\frac38,\frac58\right),\qquad
\frac{17}{20}<Q<\frac{23}{20},\qquad
C_{\rm out}<\frac7{160}<0.044\ \text{bits},\qquad
|c_{\rm in}|<\frac7{40}.}
\tag{3}
\]

In particular, the stronger individual interval in (3) implies the requested
\(q_i\in(7/20,13/20)\). Thus a strict two-letter Marton gain must have both
coordinate marginals close to balanced, must have a balanced marginal sum,
must induce little dependence between the two outputs seen by each receiver,
and cannot have large input covariance. These conditions are necessary, not
sufficient; this contribution does not produce a gain or prove that none
exists.

Two exact canonical premises are used, with disjoint roles:

1. Transaction `33a5944dca980bf94cc869c6c7dee2d04385ff58`
   (`two-letter-marton-full-support-necessity`) supplies only its two
   pre-averaging rows and their averaged universal inequality
   \(M\leq G(P_S)+2r\), recalled in (9)--(10) below.
2. Transaction `88a1004f309460f3ec1cacdae88d30f88559f9bc`
   (`marton-multiletter-foundation-repair`) supplies only its exact formula
   and directed interval for \(T=2L_{\rm RTD}\), recalled in (11). None of
   its external hypotheses (H-Marton) or (H-binary) is used here.

The new work is the exact output-correlation decomposition of \(G\), its
combination with those premises, and the directed rational pruning
certificates. This lies within the non-exclusive
`bssc-multiletter-marton-frontier` direction registered by transaction
`7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.

## 1. Exact marginal/correlation decomposition

Use the convention \(q=\Pr[X=1]\) for one channel use and define

\[
F(q):=\frac12\left[
h_2(q/2)+h_2((1-q)/2)-1
\right].
\tag{4}
\]

The governed receiver mutual informations are

\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q,
\tag{5}
\]

so \(F(q)=[I_Y(q)+I_Z(q)]/2\).

The following identities hold for every joint input law \(P_{X_1X_2}\),
without an independence assumption. Memorylessness gives

\[
\begin{aligned}
I(S;Y^2)
&=H(Y_1,Y_2)-H(Y_1,Y_2\mid X_1,X_2)\\
&=H(Y_1)+H(Y_2)-I(Y_1;Y_2)
  -H(Y_1\mid X_1)-H(Y_2\mid X_2)\\
&=I(X_1;Y_1)+I(X_2;Y_2)-I(Y_1;Y_2).
\end{aligned}
\tag{6}
\]

The same calculation applies to \(Z^2\). Therefore, for

\[
G(P_S):=\frac12\left[I(S;Y^2)+I(S;Z^2)\right],
\]

one has the exact identity

\[
\boxed{
G(P_S)=F(q_1)+F(q_2)-\frac12C_{\rm out}.}
\tag{7}
\]

This is an equality for arbitrary correlated inputs. It measures exactly how
much the two single-coordinate averages overestimate \(G\): the deficit is
one half of the two receivers' output correlations.

## 2. The master upper bound

Put

\[
h=h_2(1/4),\qquad r=h-\frac34.
\tag{8}
\]

The universal Marton-to-input-law inequality proved in canonical transaction
`33a5944dca980bf94cc869c6c7dee2d04385ff58` is

\[
M\leq G(P_S)+2r.
\tag{9}
\]

The same proof gives, before averaging, the two sharper rows

\[
\begin{aligned}
M&\leq I(S;Y^2)+2r(2-Q),\\
M&\leq I(S;Z^2)+2rQ.
\end{aligned}
\tag{9a}
\]

Combining (7) and (9) gives the correlation-sensitive envelope

\[
\boxed{
M\leq F(q_1)+F(q_2)-\frac12C_{\rm out}+2r.}
\tag{10}
\]

The exact RTD calculation and directed certificate in canonical transaction
`88a1004f309460f3ec1cacdae88d30f88559f9bc` give

\[
\begin{aligned}
0.7232857688439092313268831563011740144159620214477211104074274596056014
&<T\\
&<0.7232857688439092313268831563011740144159620214477211104074274596056016.
\end{aligned}
\tag{11}
\]

## 3. Coordinate-marginal pruning

Define the one-coordinate row envelope

\[
A(q):=I_Y(q)+2r(1-q).
\tag{12}
\]

Equations (5), (6), and (9a), followed by dropping a nonnegative output
correlation, give

\[
M\leq A(q_1)+A(q_2).
\tag{13}
\]

The reflected \(Z\)-row similarly gives

\[
M\leq A(1-q_1)+A(1-q_2),
\tag{14}
\]

because \(I_Z(q)=I_Y(1-q)\).

The function \(A\) is strictly concave. Direct differentiation gives

\[
A'(q)=1-\frac12\log_2\frac{1+q}{1-q}-2r,\qquad
A''(q)=-\frac1{\ln(2)(1-q^2)}<0.
\tag{15}
\]

Its maximizer is exact:

\[
\boxed{q_{\max}=\frac{19}{35}.}
\]

Indeed,

\[
\frac{1+q_{\max}}{1-q_{\max}}=\frac{27}{8},
\qquad
2r=\frac52-\frac32\log_2 3,
\]

where the second identity follows from
\(h_2(1/4)=2-(3/4)\log_2 3\). Substitution in (15) gives
\(A'(19/35)=0\), and strict concavity proves global maximality.

If, for example, \(q_1\leq3/8\), monotonicity up to \(q_{\max}\) and
global maximality give

\[
M\leq A(3/8)+A(19/35).
\]

The included directed checker proves the comfortable strict separation

\[
A(3/8)+A(19/35)<0.722032<T.
\tag{16}
\]

Thus \(M>T\) forces \(q_i>3/8\) for both coordinates. Applying the same
argument to (14) shows that \(1-q_i>3/8\), hence \(q_i<5/8\).

For sharpness orientation, the checker brackets the lower root of
\(A(q)+A(19/35)=T\) between \(0.379109\) and \(0.379110\). It also verifies
that \(3/8\) and \(5/13\) are Farey neighbors of order 20 and the root is
below \(5/13\). Thus \(3/8\) is the strongest denominator-at-most-20 cutoff
certified by this coordinatewise envelope.

## 4. Output-correlation pruning

The function \(F\) is reflection-symmetric, and

\[
F'(q)=\frac14\log_2
\frac{(2-q)(1-q)}{q(1+q)}.
\tag{17a}
\]

The logarithm is positive exactly for \(q<1/2\), so
\(F(q)\leq F(1/2)\). Use this in (10). If \(M>T\), then

\[
T<M\leq2F(1/2)-\frac12C_{\rm out}+2r,
\]

and therefore

\[
C_{\rm out}
<4F(1/2)+4r-2T.
\tag{17}
\]

The directed checker proves the strict comparison

\[
4F(1/2)+4r-2T
<\frac7{160}=0.04375<0.044,
\tag{18}
\]

which is the correlation assertion in (3). Numerically, only as orientation, the
left side of (18) is about \(0.04365345798524445\) bits.

## 4a. Input-covariance consequence

For either receiver \(R\in\{Y,Z\}\), the conditional output-one probability
is affine in the input bit with slope \(1/2\):

\[
\Pr[Y=1\mid X]=\frac12+\frac X2,\qquad
\Pr[Z=1\mid X]=\frac X2.
\]

Conditional independence across channel uses therefore gives

\[
\operatorname{Cov}(R_1,R_2)=\frac14c_{\rm in}.
\tag{18a}
\]

For any binary pair, all four differences between its joint table and the
product of its marginals are \(\pm\operatorname{Cov}(R_1,R_2)\). Hence

\[
\left\|P_{R_1R_2}-P_{R_1}P_{R_2}\right\|_{\rm TV}
=\frac12|c_{\rm in}|.
\tag{18b}
\]

For completeness, Pinsker's constant here follows elementarily. Aggregate
the positive-deviation cells into one event and apply the log-sum inequality.
The resulting binary relative entropy in nats has second derivative
\(1/[p(1-p)]\geq4\) in its first argument and vanishing value and first
derivative at equality. Thus, in bits,
\(D_2(P\|Q)\geq2\|P-Q\|_{\rm TV}^2/\ln2\). Applying this to both receivers
and using (18b) gives

\[
C_{\rm out}\geq\frac{c_{\rm in}^2}{\ln2}.
\tag{18c}
\]

Together with (18), this implies

\[
|c_{\rm in}|
<\sqrt{\frac7{160}\ln2}<\frac7{40}=0.175.
\tag{18d}
\]

The final strict rational comparison is certified by squaring positive
quantities in the directed checker.

## 5. Sum-marginal pruning

Equation (6), nonnegativity of output correlation, and concavity of \(I_Y\)
give

\[
I(S;Y^2)\leq I_Y(q_1)+I_Y(q_2)\leq2I_Y(Q/2).
\tag{19}
\]

The first row of (9a) therefore implies

\[
M\leq B(Q):=2I_Y(Q/2)+2r(2-Q).
\tag{20}
\]

The second row and receiver reflection give \(M\leq B(2-Q)\). Moreover,

\[
B'(Q)=1-\frac12\log_2\frac{1+Q/2}{1-Q/2}-2r,\qquad
B''(Q)=-\frac1{2\ln(2)(1-Q^2/4)}<0.
\tag{21}
\]

The checker proves \(B'(17/20)>0\) and

\[
B(17/20)<0.721880<T.
\tag{22}
\]

Thus \(Q\leq17/20\) makes the first row smaller than \(T\). If
\(Q\geq23/20\), then \(2-Q\leq17/20\) and the reflected row is smaller
than \(T\). This proves the sum interval in (3). The sharp lower crossing is
bracketed by \(0.856393<Q_*<0.856394\).

## 6. Reflected/transposed one-parameter family

There is a useful specialization of the correlation result. Suppose

\[
P_S(00)=P_S(11)=\alpha,\qquad
P_S(01)=P_S(10)=\frac12-\alpha,\qquad 0\leq\alpha\leq\frac12.
\]

Both coordinate marginals are fair. Direct channel evaluation gives

\[
P_{Y_1Y_2}
=\left(\frac{\alpha}{4},\frac{1-\alpha}{4},
       \frac{1-\alpha}{4},\frac12+\frac{\alpha}{4}\right)
\tag{23}
\]

in the order \(00,01,10,11\). The \(Z^2\) table is its bit-complement, so
the two output-pair mutual informations are equal. If

\[
J_{\rm out}(\alpha)
:=2h_2(1/4)-H_4\!\left(
\frac{\alpha}{4},\frac{1-\alpha}{4},
\frac{1-\alpha}{4},\frac12+\frac{\alpha}{4}\right),
\tag{24}
\]

then \(C_{\rm out}=2J_{\rm out}(\alpha)\). Differentiation gives

\[
J_{\rm out}'(\alpha)
=\frac14\log_2\frac{\alpha(2+\alpha)}{(1-\alpha)^2}.
\tag{25}
\]

On \((0,1/2)\), it is negative below \(1/4\) and positive above \(1/4\).
The checker proves

\[
2J_{\rm out}(1/8)>\frac7{160},\qquad
2J_{\rm out}(5/13)>\frac7{160}.
\tag{26}
\]

Monotonicity and (18) therefore give the additional necessary condition

\[
\boxed{M>T\quad\Longrightarrow\quad \frac18<\alpha<\frac5{13}}
\]

within this one-parameter family.

## Directed verification

Run from this contribution directory using only Python's standard library:

```text
python3 -I -B verify.py
```

The checker performs no writes and no network access. It:

1. verifies the two exact canonical dependency identifiers and their distinct
   roles in `claims.json`;
2. proves a rational bracket for \(\sqrt{105}\), reconstructs the exact RTD
   formula from the foundation dependency, and evaluates it with directed
   120-digit `Decimal` interval arithmetic;
3. proves (16), (18), (18d), (22), and (26), along with the two sharp root
   brackets, using outward-rounded logarithms;
4. checks the exact maximizer and Farey-neighbor arithmetic supporting the
   coordinatewise-envelope observation.

The checker certifies only the mechanical interval and rational comparisons.
Equations (6)--(15), (17)--(21), and (23)--(25), together with the elementary
Pinsker derivation, are the human-checkable information-theoretic proof.

## Limitations and attribution

- The theorem is a necessary-condition corollary for finite two-letter Marton
  laws. It is not a construction, a sufficiency theorem, a no-gain result, or
  a capacity converse.
- It bounds the input covariance \(c_{\rm in}\), not
  \(I(X_1;X_2)\) directly. Different correlated input laws may induce the same
  covariance or output-correlation value.
- The \(\alpha\)-window applies only to the explicitly displayed
  reflected/transposed one-parameter input family.
- The value is unnormalized per two-use super-symbol. Dividing by two is
  required to compare rates per original channel use.
- The exact dependencies are the canonical inequalities identified above;
  neither dependency's other claims are silently imported.
- No external source is used in the new derivation. Prior mathematical work
  is attributed by the two canonical transaction identifiers above.
