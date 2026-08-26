# Two-letter Marton pruning for one- and two-symbol super-input support

## Claim and scope

Let $P$ be the half-skew BSSC in the governed problem and let
$P^{\otimes2}$ have super-input
$S=(X_1,X_2)\in\{00,01,10,11\}$.  Assume the binary-input Marton
sum-rate theorem of Geng, Jog, Nair, and Wang: for every binary-input
two-receiver broadcast channel, Marton's private-message sum-rate equals
randomized time division.

Under that premise, the Marton sum value of every finite law for
$P^{\otimes2}$ whose
induced super-input is supported on at most two of the four symbols satisfies

\[
 R_{\rm Marton}(\text{law})<0.615\quad\text{bits}.
\]

Since the product randomized-time-division witness has value

\[
 2R_{\rm RTD}
 =2(0.361642884421954615663441578150587\ldots)
 >0.7232857688439092,
\]

any two-letter Marton witness that strictly improves the current BSSC
achievable rate must give positive mass to at least three super-input
symbols.  This is a search-space pruning theorem, not a no-gain theorem for
three- or four-symbol laws.

This supplies a structural-pruning target in the non-exclusive
`bssc-multiletter-marton-frontier` direction registered by canonical
transaction `7e1e52fe42fde37ba1964ef9ae5062daf8bb55f8`.

The result was prompted by Huang, Liu, and Liu's August 2026 construction of
a ternary-input channel with a strict two-letter Marton gain.  Their paper
explicitly leaves the binary-input case open and uses nonrectangular
two-letter architectures; see
[*Sub-optimality of Marton's Inner Bound for the Two-Receiver Broadcast
Channel*](https://arxiv.org/abs/2608.19869).  No numerical value or theorem
from that construction is used as a premise here.

## The six two-symbol supports

The six unordered pairs split into three exact symmetry classes.

1. **Adjacent pairs.**  The four Hamming-distance-one pairs differ in only
   one input coordinate.  The other coordinate produces input-independent
   output and can be discarded.  For the varying coordinate, couple the two
   receiver outputs so that $(Y,Z)$ is a binary erasure observation of the
   input with erasure probability $1/2$: the ambiguous pair is $(1,0)$,
   while $(0,0)$ and $(1,1)$ identify the input.  Receiver cooperation is
   an outer bound and the private-message capacity depends only on the two
   marginals, so every adjacent-pair Marton rate is at most $1/2$ bit.
2. **Antirepetition pair \(\{01,10\}\).**  Each receiver marginal is a
   BEC\((1/2)\), up to output relabeling: one output of probability $1/2$
   is common to both inputs and the other two identify them.  The two
   marginals may be coupled as the same erasure observation, again giving
   the cooperative outer bound $1/2$ bit.
3. **Repetition pair \(\{00,11\}\).**  This is the only nontrivial class.
   It is a binary-input receiver-skew broadcast channel, so the cited
   binary-input Marton theorem reduces its Marton sum-rate to randomized time
   division.  The next section gives a self-contained upper bound below
   $0.615$ for that functional.

Singleton support conveys no information.  These cases exhaust every support
of size at most two.

## Repetition-orbit randomized-time-division bound

Write $q=\Pr[S=0]$.  For receiver $Y^2$, input $00$ produces the
uniform distribution on four outputs and input $11$ produces the point
mass at $11$.  Thus

\[
 J(q)=I_q(S;Y^2)
 =H_2\!\left(\frac q4,\frac q4,\frac q4,
                   1-\frac{3q}{4}\right)-2q,
 \tag{1}
\]

while $I_q(S;Z^2)=J(1-q)$.  For a randomized-time-division law, let
$q_w=\Pr[S=0\mid W=w]$, let $\bar q=\mathbb E q_W$, and in each
component direct the private layer to whichever receiver has the larger
mutual information.  Then

\[
\begin{aligned}
M
&\le \frac{I(W;Y^2)+I(W;Z^2)}2
   +\mathbb E\max\{J(q_W),J(1-q_W)\}\\
&=\frac{J(\bar q)+J(1-\bar q)}2
  +\frac12\mathbb E|J(q_W)-J(1-q_W)|\\
&\le J(1/2)+\frac12\max_{0\le q\le1}|J(q)-J(1-q)|.
\tag{2}
\end{aligned}
\]

The last step uses concavity of $J$: the sum
$J(q)+J(1-q)$ is concave and reflection symmetric, hence maximized at
$q=1/2$.

For $q\in[1/2,1]$, put $D(q)=J(1-q)-J(q)$.  Direct differentiation
gives

\[
 J'(q)=\frac34\log_2\frac{4-3q}{q}-2,
 \qquad
 J''(q)=-\frac{3}{\ln 2\;q(4-3q)},
\]

and therefore

\[
 D''(q)=-\frac3{\ln2}
 \left(
 \frac1{(1-q)(1+3q)}-\frac1{q(4-3q)}
 \right)<0
 \quad(q>1/2),
\tag{3}
\]

because $q(4-3q)-(1-q)(1+3q)=2q-1>0$.  Also
$D(1/2)=D(1)=0$, so $D\ge0$ and is concave on this half interval;
antisymmetry then gives
$\max|J(q)-J(1-q)|=\max_{[1/2,1]}D(q)$.

At the exact rational point $q_0=17/20$, concavity supplies the global
tangent bound

\[
 D(q)\le D(q_0)+D'(q_0)(q-q_0).
\]

The included directed-Decimal checker proves

\[
 J(1/2)<0.549,qquad D'(q_0)<0,qquad
 \max_{[1/2,1]}D<0.132.
\]

Equation (2) consequently gives $M<0.549+0.132/2=0.615$.

## Reproduction

Run from this contribution directory with only the Python standard library:

```text
python3 -I -B verify.py
```

The checker uses exact `Fraction` arithmetic to build both product receiver
marginals, classify all six two-symbol supports, and verify the displayed
adjacent, antirepetition, and repetition transition structures.  It then uses
80-digit directed `Decimal` intervals for (1)--(3), checks the tangent bound,
and requires the final upper endpoint to be strictly below `0.615`.  It also
checks the strict separation from the two-letter RTD baseline.  The interval
calculation is mechanical corroboration; the support reduction, cooperation
arguments, binary-input Marton premise, and calculus proof are mathematical.

## Provenance and limitations

The binary-input Marton theorem used as an explicit external premise is:
Yanlin Geng, Varun Jog, Chandra Nair, and Zizhou Vincent Wang, *An Information
Inequality and Evaluation of Marton's Inner Bound for Binary Input Broadcast
Channels*, IEEE Transactions on Information Theory 59 (2013),
[arXiv:1001.1468](https://arxiv.org/abs/1001.1468).

The theorem does not exclude a two-letter Marton improvement whose input law
uses three or four super-input symbols; it gives no positive-gain witness,
no multiletter tensorization, no capacity converse, and no improvement to the
governed capacity interval.  The `0.615` bound is deliberately coarse; its
purpose is a robust strict separation from $2R_{\rm RTD}$, not exact
evaluation of the repetition subchannel.  The proof and checker were prepared
by an OpenAI Codex solver agent at Robert Raynor's request.
