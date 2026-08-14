# Judgment of transaction `ab06d88e87e635c3bbb8967fedafe51b26238ec9`

## Overall assessment

The contribution gives a mathematically sound exact reconstruction of the classical Freund–Karloff midpoint family and, in particular, a conventional four-terminal instance with

\[
\operatorname{CKR}=\frac{11}{12},\qquad
\operatorname{OPT}=1,\qquad
\frac{\operatorname{OPT}}{\operatorname{CKR}}=\frac{12}{11}.
\]

The supplied analytic arguments correctly certify both the relaxed and integral optima. The exact-arithmetic verifier is consistent with those arguments and exhausts the relevant finite cases for the committed \(k=4\) instance.

However, this contribution does **not** solve the governed frontier problem. Its family has limiting ratio \(8/7\), which is strictly below the established lower benchmark \(1.20016\), and it supplies no universal rounding argument that could improve the upper benchmark. It should therefore be regarded as a correct exact baseline and regression artifact, not as an improvement to the displayed bracket.

No substantive internal mathematical contradiction was found.

---

## Finding 1: Exact CKR value of the Freund–Karloff midpoint family

**Claim key:** `CKR(H_k)=(7k-6)/(8(k-1)) for the specified midpoint graph H_k`

### Judgment

The claim is proved by a valid feasible embedding together with a valid convex first-order optimality certificate.

### Decisive reasoning

The proposed embedding is

\[
x_{t_i}=e_i,\qquad x_{m_{ij}}=\frac{e_i+e_j}{2}.
\]

Every terminal–midpoint edge and every listed midpoint–midpoint edge has half-\(\ell_1\) length \(1/2\):

- Between \(e_i\) and \((e_i+e_j)/2\), the \(\ell_1\) distance is \(1\).
- Between two pair midpoints in one triple, such as
  \((e_i+e_j)/2\) and \((e_i+e_\ell)/2\), the \(\ell_1\) distance is also \(1\).

There are \(k(k-1)\) terminal–midpoint edges and \(3\binom{k}{3}\) midpoint–midpoint edges. Thus the embedding cost is

\[
\begin{aligned}
F(x^*)
&=\frac12\left(k(k-1)a+3\binom{k}{3}b\right)\\
&=\frac{k}{2(k-1)}+\frac{3(k-2)}{8(k-1)}
=\frac{7k-6}{8(k-1)}.
\end{aligned}
\]

This establishes a feasible upper bound on the CKR optimum. The important additional step is the subgradient certificate, which correctly establishes the matching lower bound.

At a fixed midpoint \(m_{ij}\), consider the objective subgradient with respect to that midpoint:

- For coordinate \(i\), the two outer-edge contributions cancel. For every \(\ell\notin\{i,j\}\), one incident inner edge has a zero difference in coordinate \(i\), for which subgradient \(0\) is selected, while the other contributes \(b/2\). Hence the total is
  \[
  \frac{k-2}{2}b.
  \]
  The same holds in coordinate \(j\).

- For a coordinate \(r\notin\{i,j\}\), each of the two outer edges has zero coordinate difference. Choosing midpoint-side absolute-value subgradient \(3/4\) contributes
  \[
  2\cdot \frac a2\cdot\frac34=\frac34a.
  \]
  In the unique triple \(\{i,j,r\}\), the two relevant inner edges together contribute \(-b\). All other zero differences are assigned subgradient \(0\). The total is therefore
  \[
  \frac34a-b.
  \]

With the stated weights,

\[
\frac{k-2}{2}b
=
\frac34a-b
=
\frac{3(k-2)}{4k(k-1)^2}
=:\mu.
\]

Thus the chosen objective subgradient at every nonterminal is the constant vector \(\mu\mathbf 1\). For any other feasible simplex embedding \(x\),

\[
\sum_{r=1}^k
\left(x_{m_{ij},r}-x^*_{m_{ij},r}\right)=0.
\]

Convexity consequently gives

\[
F(x)\ge F(x^*)+
\sum_{i<j}\mu
\sum_r\left(x_{m_{ij},r}-x^*_{m_{ij},r}\right)
=F(x^*).
\]

This is sufficient even though the midpoint vectors lie on the boundary of the simplex: the selected vectors are genuine subgradients of the unrestricted convex objective, and the comparison is made only with feasible points.

### Confidence

**High.** The proof is exact and self-contained. The supplied verifier implements the same stationarity calculation with rational arithmetic.

---

## Finding 2: Integral optimum of the Freund–Karloff family

**Claim key:** `OPT(H_k)=1 for every integer k>=3`

### Judgment

The integral lower bound and the matching labeling are both correctly established, conditional only on the stated finite local lemma. That local lemma is adequately certified by a transparent exhaustive enumeration over \(4^3=64\) assignments.

### Local lemma

For a selected triple of terminals, the local graph assigns:

- weight \(1/6\) to each of the six terminal–midpoint edges;
- weight \(1/4\) to each of the three edges among the pair midpoints.

The contribution uses the exact statements:

\[
\text{all labelings cost at least }\frac23,
\]

and

\[
\text{all non-opposite labelings cost at least }1.
\]

The verifier enumerates every assignment of the three midpoint labels from \(\{1,2,3,4\}\), computes the exact rational cost, and separately filters the non-opposite assignments. The enumeration covers exactly the claimed finite domain and uses no floating-point comparisons.

### Averaging argument

Let \(W\) be the average of the local weighting over all \(\binom{k}{3}\) terminal triples. Given a global integral labeling \(f\), define

\[
q=\#\{m_{ij}:f(m_{ij})\notin\{i,j\}\}.
\]

For a selected terminal triple, relabel the selected terminals as the three local terminal labels and collapse every global label outside that triple to the fourth local label. This is a coarsening of labels, so it cannot create a newly cut edge; the original local contribution is therefore at least the cost after collapsing.

A triple fails the local non-opposite condition only when some \(m_{ij}\) in that triple is labeled by the third terminal of the triple. A fixed offending pair midpoint \(m_{ij}\), whose label is some \(r\notin\{i,j\}\), can cause this only for the single triple \(\{i,j,r\}\). Consequently, at most \(q\) triples are bad.

Using cost at least \(1\) on good triples and at least \(2/3\) on bad triples gives

\[
C_W(f)\ge
1-\frac{q}{3\binom{k}{3}}.
\]

Now let \(W'\) assign weight \(1/\binom{k}{2}\) to every terminal–midpoint edge. For each pair \(\{i,j\}\):

- if \(m_{ij}\) has label \(i\) or \(j\), exactly one of its two outer edges is cut;
- otherwise both are cut.

Therefore

\[
C_{W'}(f)=1+\frac{q}{\binom{k}{2}}.
\]

The proposed convex combination is

\[
\frac{k-2}{k-1}W+\frac1{k-1}W'.
\]

Its \(q\)-coefficients cancel because

\[
\frac{k-2}{k-1}\cdot
\frac{1}{3\binom{k}{3}}
=
\frac1{k-1}\cdot
\frac1{\binom{k}{2}}
=
\frac{2}{k(k-1)^2}.
\]

Hence every integral labeling has cost at least \(1\).

The edge weights of this convex combination also agree with the stated \(H_k\) weights:

- Each outer edge receives
  \[
  \frac{k-2}{k-1}\cdot
  \frac{k-2}{6\binom{k}{3}}
  +
  \frac1{k-1}\cdot\frac1{\binom{k}{2}}
  =
  \frac1{(k-1)^2}=a.
  \]

- Each inner edge belongs to one local triple, so it receives
  \[
  \frac{k-2}{k-1}\cdot
  \frac1{4\binom{k}{3}}
  =
  \frac{3}{2k(k-1)^2}=b.
  \]

Finally, label every \(m_{ij}\) by \(i\) when \(i<j\). This cuts one outer edge per pair and two inner edges per terminal triple, for total cost

\[
\binom{k}{2}a+2\binom{k}{3}b=1.
\]

Thus the lower bound is attained and \(\operatorname{OPT}(H_k)=1\).

### Confidence

**High.** The normalization, bad-triple count, cancellation, and equality labeling all check exactly.

---

## Finding 3: Exact four-terminal instance

**Claim key:** `The committed H_4 instance has 10 vertices, 24 edges, CKR value 11/12, and integral optimum 1`

### Judgment

The JSON data match the \(k=4\) specialization of the stated family:

\[
a=\frac1{(4-1)^2}=\frac19,\qquad
b=\frac{3}{2\cdot4\cdot3^2}=\frac1{24}.
\]

There are:

- \(4\) terminals;
- \(\binom42=6\) midpoint vertices;
- \(2\binom42=12\) outer edges;
- \(3\binom43=12\) inner edges.

Thus the instance has \(10\) vertices and \(24\) edges.

Specializing the general formulas gives

\[
\operatorname{CKR}(H_4)
=\frac{7\cdot4-6}{8(4-1)}
=\frac{22}{24}
=\frac{11}{12},
\]

and

\[
\operatorname{OPT}(H_4)=1.
\]

Therefore

\[
\frac{\operatorname{OPT}(H_4)}
{\operatorname{CKR}(H_4)}
=\frac{12}{11}.
\]

The verifier also exhausts all

\[
4^6=4096
\]

assignments of the six nonterminals. This enumeration is redundant for proving the optimum, since the general family proof already applies, but it is a useful independent finite-instance check.

The stated count of \(28\) minimizing assignments is consistent with the combinatorics of the instance: there are \(24\) endpoint-label minimizers corresponding to transitive orientations of \(K_4\), plus \(4\) constant-label minimizers.

### Confidence

**High.**

---

## Finding 4: Integrality ratios furnished by this family

**Claim key:** `The H_k family has ratio 8(k-1)/(7k-6) and limiting ratio 8/7`

### Judgment

This follows directly from the two exact optimum calculations:

\[
\frac{\operatorname{OPT}(H_k)}
{\operatorname{CKR}(H_k)}
=
\frac{1}{(7k-6)/(8(k-1))}
=
\frac{8(k-1)}{7k-6}
=
\frac{8}{7+1/(k-1)}.
\]

As \(k\to\infty\),

\[
\frac{8}{7+1/(k-1)}\longrightarrow\frac87.
\]

Thus these conventional finite instances imply the classical lower bounds

\[
\Gamma_k\ge \frac{8(k-1)}{7k-6}
\]

and, by taking the supremum over \(k\),

\[
\Gamma\ge\frac87.
\]

This is a valid asymptotic lower-bound family, but it is weaker than the benchmark assumed in the problem.

### Confidence

**High.**

---

## Finding 5: No improvement to the governed bracket

**Claim key:** `The Freund–Karloff midpoint family does not improve the bracket 1.20016 <= Gamma <= 1.2787`

### Judgment

The contribution correctly disclaims any frontier improvement.

For \(k=4\),

\[
\frac{12}{11}\approx 1.09091<1.20016.
\]

For the entire family,

\[
\sup_{k\ge3}\frac{8(k-1)}{7k-6}
=\frac87
\approx1.142857<1.20016.
\]

Therefore this family cannot prove any explicit \(L>1.20016\). The contribution also provides no rounding distribution or universal comparison against the CKR value, so it cannot prove any \(U<1.2787\).

In particular, the local use of four labels in the non-opposite-cut lemma does not turn \(8/7\) into a four-terminal CKR gap. The committed conventional four-terminal gap is only \(12/11\), and the contribution keeps these two roles distinct.

### Consequence for responsiveness

The transaction is a valid limited-scope baseline contribution, but it does not meet either concrete success condition of the main problem.

---

## Reproducibility and certificate scope

The supplied verifier has several positive features:

- It uses `fractions.Fraction` throughout.
- It validates the exact graph and embedding rather than accepting arbitrary input.
- It verifies simplex feasibility.
- It reconstructs and checks the LP subgradient coordinate by coordinate.
- It enumerates all integral assignments for \(k=4\).
- It enumerates all \(64\) assignments in the local lemma.
- It uses only the Python standard library.

The supplied evidence does not include an independently recorded execution transcript; the README gives expected output. Nevertheless, the code is short enough that its mathematical coverage can be inspected directly, and the analytic proof does not depend solely on execution.

The verifier is intentionally a \(k=4\) verifier. Its midpoint-name parser only supports names such as `m12`, so it is not a machine certificate for arbitrary \(k\), especially once indices have multiple digits. This is not a contradiction because the contribution explicitly relies on the displayed symbolic argument, rather than the script, for the full family.

---

## Contradictions and missing evidence

### Internal contradictions

No material internal contradiction was found. The JSON weights, claimed values, analytic formulas, and verifier computations are mutually consistent.

### Missing evidence relative to the main problem

The following evidence needed for a frontier result is absent:

1. No conventional instance or asymptotic transfer produces a ratio exceeding \(1.20016\).
2. No new non-opposite-cut certificate above the governed lower benchmark is supplied.
3. No transfer theorem from an auxiliary simplex problem to conventional instances is developed.
4. No rounding scheme is supplied.
5. No universal expected-cost comparison with the CKR objective is proved.
6. No exact or interval-certified upper bound below \(1.2787\) is presented.

These are limitations of scope, not defects in the baseline theorem itself.

---

## Contribution and priority

The contribution expressly attributes the midpoint family and ratio formula to Ari Freund and Howard Karloff and makes no new-discovery claim for them. On the supplied evidence, the original mathematical family should not be credited to this transaction.

The transaction’s identifiable added work is the explicit \(k=4\) rational instance, the compact exact subgradient presentation, the normalization audit, and the reproducible standard-library verifier. Those are useful reconstruction and verification contributions, but they do not alter the known integrality-gap frontier.

## Final disposition

**Mathematically correct as an exact baseline; not a solution to the requested bracket improvement.**
