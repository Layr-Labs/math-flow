## `multiway-cut-ckr-gap/exact-freund-karloff-k4-baseline`

**Verdict: VALID**

The mathematical claims are established by the supplied exact construction and certificates.

### 1. Instance structure

For \(k=4\), the construction has

\[
4+\binom42=10
\]

vertices. It has

\[
2\binom42=12
\]

terminal–midpoint edges and

\[
3\binom43=12
\]

midpoint–midpoint edges, hence \(24\) edges total. The JSON lists exactly these edges, with

\[
a=\frac1{(4-1)^2}=\frac19,\qquad
b=\frac3{2\cdot4\cdot(4-1)^2}=\frac1{24}.
\]

All weights are nonnegative rational numbers, and the four terminals are distinct. Thus it is a conventional finite four-terminal Multiway Cut instance.

### 2. CKR feasible value

The proposed embedding

\[
x_{m_{ij}}=\frac{e_i+e_j}{2}
\]

lies in \(\Delta_k\), while terminals have the required embeddings \(e_i\).

Every terminal–midpoint edge and every listed midpoint–midpoint edge has half-\(\ell_1\) length \(1/2\). Therefore the embedding cost is

\[
\frac12\left(k(k-1)a+3\binom{k}{3}b\right).
\]

Substitution gives

\[
\frac{k}{2(k-1)}
+\frac{3(k-2)}{8(k-1)}
=\frac{7k-6}{8(k-1)}.
\]

This proves the corresponding CKR upper bound.

### 3. CKR optimality certificate

The supplied subgradient certificate is valid.

At a fixed midpoint \(m_{ij}\):

- In coordinate \(i\), the two outer-edge contributions cancel. For each \(\ell\notin\{i,j\}\), exactly one incident inner edge contributes \(b/2\), giving
  \[
  g_{m_{ij},i}=\frac{k-2}{2}b.
  \]
  The same holds in coordinate \(j\).

- For \(r\notin\{i,j\}\), the two zero-coordinate outer-edge subgradients contribute
  \[
  2\cdot \frac a2\cdot\frac34=\frac34a.
  \]
  The two inner edges associated with \(\ell=r\) contribute \(-b/2\) each, hence
  \[
  g_{m_{ij},r}=\frac34a-b.
  \]

With the stated values of \(a,b\),

\[
\frac{k-2}{2}b
=\frac34a-b
=\frac{3(k-2)}{4k(k-1)^2}
=:\mu.
\]

Thus the selected objective subgradient at every nonterminal is \(\mu\mathbf 1\). For every other feasible embedding \(x\), convexity yields

\[
F(x)\ge F(x^*)+
\sum_{i<j}\mu\mathbf1\cdot
(x_{m_{ij}}-x^*_{m_{ij}}).
\]

Each dot product vanishes because both vectors have coordinate sum one. Hence \(F(x)\ge F(x^*)\), proving

\[
\operatorname{CKR}(H_k)=\frac{7k-6}{8(k-1)}.
\]

The argument remains valid at the boundary of the simplex because the chosen values are legitimate ambient subgradients of the absolute-value terms.

### 4. Local integral lemma

For the three-midpoint local graph, let \(q_{\mathrm{loc}}\) be the number of midpoints whose label is not one of its two endpoint labels. The outer-edge cost is

\[
\frac{3+q_{\mathrm{loc}}}{6}.
\]

The midpoint triangle has:

- zero cut edges if all three midpoint labels agree;
- at least two cut edges otherwise.

For an unrestricted labeling:

- If all labels agree, no label is an endpoint label for all three pairs, so \(q_{\mathrm{loc}}\ge1\), giving cost at least \(4/6=2/3\).
- Otherwise the outer cost is at least \(1/2\) and the triangle cost at least \(2(1/4)=1/2\), giving at least \(1\).

The lower bound \(2/3\) is attained, for example, by assigning all three midpoints label \(1\).

For a non-opposite labeling, if all labels agree, their only common permitted label is \(4\), which cuts all six outer edges and costs \(1\). If they do not all agree, the preceding \(1/2+1/2\) bound applies. Hence the non-opposite minimum is exactly \(1\).

Thus the enumerated local minima are correct.

### 5. Averaging argument for the integral lower bound

Let \(N=\binom{k}{3}\), and let \(W\) be the average of the local weighted graph over all terminal triples.

For a labeling \(f\), let

\[
q=\#\{m_{ij}: f(m_{ij})\notin\{i,j\}\}.
\]

After collapsing labels outside a selected triple to label \(4\), cut edges can only disappear. A triple is non-opposite unless one of its pair vertices is labeled by the third terminal in that triple. Each offending \(m_{ij}\) can make only the unique triple

\[
\{i,j,f(m_{ij})\}
\]

bad. Hence the number \(B\) of bad triples satisfies \(B\le q\). The local bounds give

\[
C_W(f)
\ge \frac{N-B}{N}\cdot1+\frac{B}{N}\cdot\frac23
\ge 1-\frac{q}{3N}.
\]

For \(W'\), which assigns weight \(1/\binom{k}{2}\) to every terminal–midpoint edge, each pair contributes one cut edge if its midpoint has an endpoint label and two otherwise. Therefore

\[
C_{W'}(f)=1+\frac{q}{\binom{k}{2}}.
\]

The edge weights in

\[
\frac{k-2}{k-1}W+\frac1{k-1}W'
\]

are exactly those of \(H_k\):

- each outer edge has weight
  \[
  \frac{k-2}{k-1}\frac1{k(k-1)}
  +\frac1{k-1}\frac1{\binom{k}{2}}
  =\frac1{(k-1)^2}=a;
  \]
- each inner edge has weight
  \[
  \frac{k-2}{k-1}
  \frac1{4\binom{k}{3}}
  =\frac3{2k(k-1)^2}=b.
  \]

Moreover, the \(q\)-coefficients cancel exactly:

\[
\frac{k-2}{k-1}\frac1{3\binom{k}{3}}
=
\frac1{k-1}\frac1{\binom{k}{2}}
=
\frac{2}{k(k-1)^2}.
\]

Consequently every integral labeling has cost at least \(1\).

### 6. Attainment of the integral bound

Label each \(m_{ij}\) by \(i\) for \(i<j\). This cuts one outer edge per pair and two inner edges per terminal triple. Its cost is

\[
\binom{k}{2}a+2\binom{k}{3}b
=\frac{k}{2(k-1)}+\frac{k-2}{2(k-1)}
=1.
\]

Thus

\[
\operatorname{OPT}(H_k)=1.
\]

### 7. Ratio and \(k=4\) specialization

Therefore

\[
\frac{\operatorname{OPT}(H_k)}{\operatorname{CKR}(H_k)}
=\frac{8(k-1)}{7k-6}
=\frac8{7+1/(k-1)}.
\]

For \(k=4\),

\[
\operatorname{CKR}=\frac{28-6}{8\cdot3}
=\frac{11}{12},\qquad
\operatorname{OPT}=1,
\]

so the ratio is \(12/11\), as claimed.

The construction does not improve the governed \(1.20016\) lower benchmark: its ratios approach only \(8/7\). The submission states this limitation correctly. Historical attribution and priority are outside this correctness audit.
