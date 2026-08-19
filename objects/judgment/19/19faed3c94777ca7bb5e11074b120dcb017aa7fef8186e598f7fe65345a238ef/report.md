## `replicable-pac-sample-complexity/one-coordinate-half-interval-matching-bound`

**Verdict: invalid**

The two numbered upper- and lower-bound theorems are supported by the supplied argument. However, the declared claim also asserts an unqualified restricted sample complexity of  
\(\Theta(1/(\varepsilon\rho))\) throughout \(0<\delta,\rho\le 1/20\). That assertion is false when \(\delta\) is allowed to vary: accuracy alone forces additional growth of order \(\varepsilon^{-1}\log(1/\delta)\). Because the exact declared claim includes this materially stronger conclusion, it cannot be accepted as stated.

### 1. Half-interval geometry

For \(0\le t\le\ell=(k-1)/2\), shifting an interval of length \(\ell\) by \(t\) removes \(t\) points and adds \(t\) points. Thus

\[
\Pr_D[h_i\ne h_{i+t}]=\frac{2t}{k}.
\]

For a fixed orientation, the removed and added segments both grow monotonically with \(t\), establishing the asserted nesting. Oddness of \(k\) ensures every hypothesis index has a unique orientation and distance \(d_{\rm cyc}\le\ell\). Equations (1)–(2) are therefore correct.

### 2. Upper bound

The upper-bound construction and analysis are valid.

- A partition into \(q=\lceil k/L\rceil\) nonempty consecutive blocks of size at most \(L\) exists.
- Since \(\varepsilon<1\), \(L\le\ell+1<k\), so \(q\ge2\) and the partition has exactly \(q\) boundary edges.
- If a version space lies in one block, its representative is at circular distance at most \(L-1\) from the target, hence has error at most
  \[
  \frac{2(L-1)}k\le\varepsilon.
  \]
- If a consistent hypothesis has error \(>\varepsilon\), its circular distance is at least \(L\). When \(L\le\ell\), nesting implies that either \(h_{i+L}\) or \(h_{i-L}\) is consistent. This gives
  \[
  \Pr[\operatorname{err}_i(A(S;U))>\varepsilon]
  \le 2(1-2L/k)^n
  \le 2e^{-\varepsilon n}.
  \]
  When \(L>\ell\), no bad hypothesis exists, as claimed.
- For the version-space radius,
  \[
  \Pr[R(S)\ge t]\le2e^{-2nt/k},
  \]
  and summing the integer tail gives
  \[
  \mathbb E R(S)
  \le\frac{2}{e^{2n/k}-1}\le\frac{k}{n}.
  \]
- The union of shortest paths from the target to the version space uses at most \(2R(S)\) edges. Under a uniform shift, each edge is a boundary with probability \(q/k\). Hence
  \[
  \Pr[V(S)\text{ crosses the target block}]
  \le\frac{2q}{n}.
  \]
  A union bound over two independent samples sharing the same shift gives disagreement probability at most \(4q/n\).

Finally,

\[
q<\frac{2}{\varepsilon}+1\le\frac{3}{\varepsilon}
\]

is correct for \(0<\varepsilon<1\). Thus the proved upper bound is

\[
n=O\!\left(
\max\left\{
\frac1\varepsilon\log\frac1\delta,\,
\frac1{\varepsilon\rho}
\right\}\right).
\]

### 3. Lower bound

The supplied lower-bound proof is also valid.

#### Modes

For fixed target and seed, the output distribution has finite support because \(X=\mathbb Z_k\) is finite. If \(p_{i,r}\) is its maximum mass and \(c_{i,r}\) its collision probability, then

\[
c_{i,r}=\sum_f\mu_{i,r}(f)^2\le p_{i,r}.
\]

Replicability consequently gives

\[
\mathbb E_r(1-p_{i,r})\le\rho.
\]

If the mode is inaccurate, the fixed-seed failure probability is at least its mass. Therefore

\[
\Pr_{i,r}[\operatorname{err}_i(m_r(i))>\varepsilon]
\le\delta+\rho.
\]

No improperness or seed-quantifier issue is overlooked here.

#### Symmetric coupling

For \(1\le n<k/24\),

\[
M=\left\lfloor\frac{k}{12n}\right\rfloor
\]

satisfies \(k/(24n)\le M\le k/(12n)\le k/12\). The probability that targets \(i\) and \(i+M\) produce identical labeled samples is

\[
\alpha=(1-2M/k)^n\ge1-\frac{2nM}{k}\ge\frac56.
\]

The kernel \(K_S\) is well-defined:

- \(i+M\), \(i-M\), and \(i\) are distinct because \(1\le M<k/2\) and \(k\) is odd;
- its diagonal is nonnegative since \(2\gamma\le4/5\);
- it is symmetric and hence doubly stochastic.

Thus the second target has the correct independent uniform target/sample marginal, while the coupled labeled inputs agree exactly. For a shared fixed seed, if the two modes differ, the common output misses at least one mode. Applying the mode-miss bounds to both correct marginals yields

\[
\Pr[m_r(i)\ne m_r(v)]\le2\rho.
\]

The averaged transition law is uniform on \(\{-M,0,M\}\), so

\[
b=\Pr[m_r(i)\ne m_r(i+M)]\le3\rho.
\]

#### Long path

With

\[
t=\left\lfloor\frac{\varepsilon k}{M}\right\rfloor+1,
\]

one has

\[
\varepsilon k<tM\le\varepsilon k+M
\le\frac{k}{4}+\frac{k}{12}<\frac{k}{2}.
\]

Thus the endpoint hypotheses have disagreement \(2tM/k>2\varepsilon\). Their modes cannot be equal while both modes are \(\varepsilon\)-accurate. A union bound over endpoint inaccuracies and the \(t\) mode edges gives

\[
1\le2(\delta+\rho)+tb.
\]

Since \(t\le24\varepsilon n+1\) and \(b\le3\rho\),

\[
n\ge\frac{1-2\delta-5\rho}{72\varepsilon\rho}.
\]

For \(\delta,\rho\le1/20\), the numerator is at least \(13/20>72/120\), yielding

\[
n\ge\frac1{120\varepsilon\rho}.
\]

The separately treated \(n=0\) case is also excluded: \(h_i\) and \(h_{i+\ell}\) disagree on \((k-1)/k>2\varepsilon\), so their \(\varepsilon\)-accuracy output sets are disjoint, while a zero-sample learner has the same output law for both targets.

### 4. Decisive defect: omitted confidence dependence

The conclusion

\[
\text{“the restricted sample complexity is }
\Theta(1/(\varepsilon\rho))\text{”}
\]

is not valid uniformly over the stated range \(0<\delta\le1/20\).

Indeed, choose two targets whose disagreement probability is \(p>2\varepsilon\), with \(p<1\). Let \(E\) be the event that none of the \(n\) sample points falls in their disagreement set. Then

\[
\Pr(E)=(1-p)^n.
\]

Conditional on \(E\), the labeled-sample distributions under the two targets are identical. Since no classifier can have error at most \(\varepsilon\) against both targets when their mutual disagreement is \(>2\varepsilon\), the two conditional failure probabilities sum to at least one. Consequently, for at least one target,

\[
\Pr[\text{failure}]\ge\frac12(1-p)^n.
\]

Thus \((\varepsilon,\delta)\)-accuracy requires

\[
n\ge
\frac{\log(1/(2\delta))}{-\log(1-p)}.
\]

In the claim’s parameter regime, one may take  
\(d=\lfloor\varepsilon k\rfloor+1\) and \(p=2d/k\). The condition
\(k\ge1/(5\varepsilon\rho)\), with \(\rho\le1/20\), gives
\(\varepsilon k\ge4\), so \(d\le\ell\) and

\[
2\varepsilon<p\le\frac52\varepsilon.
\]

Since \(\varepsilon\le1/4\), this implies

\[
-\log(1-p)\le\frac{p}{1-p}\le\frac{20}{3}\varepsilon,
\]

and hence

\[
n\ge
\frac{3}{20\varepsilon}\log\frac1{2\delta}.
\]

Therefore the fixed-uniform-distribution sample complexity necessarily has confidence dependence. What the supplied evidence supports is, up to constants in the stated lower-bound regime,

\[
\Theta\!\left(
\max\left\{
\frac1{\varepsilon\rho},
\frac1\varepsilon\log\frac1\delta
\right\}
\right),
\]

although the confidence lower bound above was not included in the submitted proof.

Accordingly, the claimed \(\Theta(1/(\varepsilon\rho))\) conclusion is correct only under an additional condition such as

\[
\log(1/\delta)=O(1/\rho),
\]

in particular when \(\delta\) and \(\rho\) are treated as fixed constants. No such qualification appears in the exact declared conclusion.

### 5. Scope of the logarithmic-\(k\) discussion

The fixed-uniform-\(D\) upper bound does establish that increasing \(k\) alone does not create a \(\log k\) factor for this particular restricted experiment. It does **not**, by itself, rule out greater hardness for the same class under a nonuniform adversarial distribution. The stated worst-case corollary

\[
n_{\mathrm{rep}}(k,\varepsilon,\delta,\rho)
\ge\frac1{120\varepsilon\rho}
\]

is valid for odd \(k\) in the stated regime, but it is only a lower bound and does not upper-bound the unrestricted worst-case complexity of \(H_k\).
