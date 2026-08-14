# Mathematical judgment

## Overall assessment

The contribution gives a convincing, self-contained proof of a **distribution-restricted, one-coordinate theorem** for cyclic half-intervals under the uniform distribution. Both principal bounds appear mathematically correct:

\[
\frac{1}{120\varepsilon\rho}
\;\le\;
n_{\mathrm{unif}}(H_k,\varepsilon,\delta,\rho)
\;\le\;
\max\!\left\{
\frac1\varepsilon\log\frac2\delta,\,
\frac{12}{\varepsilon\rho}
\right\}
\]

in the stated lower-bound parameter regime, where the left side also requires odd \(k\ge 1/(5\varepsilon\rho)\).

The upper-bound proof correctly uses a randomly shifted coarse partition of the cycle and concentration of the version space. The lower-bound proof contains a substantive and apparently valid symmetric coupling: two different targets are coupled so that their labeled samples are identical while both target/sample marginals remain correct. Replicability then forces neighboring target-dependent output modes to change rarely, while accuracy forces a change over a sufficiently long path.

This is a meaningful restricted result, but it does **not** close or improve the \(\log |H|\) exponent gap in the original worst-case problem. Two interpretive claims need qualification:

1. The asserted \(\Theta(1/(\varepsilon\rho))\) characterization is only justified when the confidence term satisfies
   \[
   \log(2/\delta)=O(1/\rho),
   \]
   including the intended regime of fixed small \(\delta,\rho\). It is not established uniformly for arbitrarily small \(\delta\).

2. The uniform-distribution upper bound rules out a growing \(\log k\) factor for this **fixed uniform experiment**, but it does not by itself rule out a stronger lower bound for the same class \(H_k\) under a different, adversarially chosen distribution.

Subject to those scope qualifications, the mathematical core is strong and warrants high confidence.

---

## Finding 1: Uniform cyclic half-intervals admit a proper \(O((\log(1/\delta)+1/\rho)/\varepsilon)\)-sample replicable learner

**Claim key:** `uniform-cyclic-half-interval-proper-replicable-upper-bound`

**Judgment:** Proven by the supplied argument.

For odd \(k\), let \(H_k\) be the \(k\) cyclic translates of an interval of length \((k-1)/2\), and fix \(D\) to be uniform on \(\mathbb Z_k\). The contribution constructs a proper learner satisfying accuracy and replicability once

\[
n\ge
\max\left\{
\frac1\varepsilon\log\frac2\delta,\,
\frac{4q}{\rho}
\right\},
\qquad
q=\left\lceil \frac{k}{\lfloor\varepsilon k/2\rfloor+1}\right\rceil.
\]

The simplification \(q<2/\varepsilon+1\le 3/\varepsilon\) is correct, yielding the sufficient condition \(n\ge 12/(\varepsilon\rho)\) for replicability.

### Decisive geometric facts

For targets at cyclic distance \(t\le (k-1)/2\), the disagreement probability is

\[
\Pr_D[h_i\ne h_{i+t}]=\frac{2t}{k}.
\]

The relevant disagreement sets are nested as \(t\) increases in either orientation. These facts correctly imply:

- a hypothesis at cyclic distance at most
  \[
  L-1=\left\lfloor\frac{\varepsilon k}{2}\right\rfloor
  \]
  has error at most \(\varepsilon\);
- if any consistent hypothesis has error greater than \(\varepsilon\), then one of \(h_{i+L}\) or \(h_{i-L}\) is also consistent.

The second point follows because consistency of a farther hypothesis means that the sample avoids its disagreement set, and hence also avoids the nested disagreement set of the nearer shift.

### Accuracy argument

The cycle is partitioned into \(q\) consecutive blocks of length at most \(L\), and the seed chooses a uniform cyclic shift of this partition and its representatives.

If the version space lies in one block, that block contains the true target, and its representative is within cyclic distance \(L-1\). Thus the output has error at most \(\varepsilon\).

Otherwise the learner outputs a consistent hypothesis. A bad consistent hypothesis can exist only if \(h_{i+L}\) or \(h_{i-L}\) is consistent. Each such event has probability

\[
\left(1-\frac{2L}{k}\right)^n.
\]

Consequently,

\[
\Pr[\operatorname{err}_i(A(S;U))>\varepsilon]
\le
2\left(1-\frac{2L}{k}\right)^n
\le 2e^{-\varepsilon n}.
\]

The displayed accuracy threshold follows. This part has the correct quantifiers and does not rely on properness beyond the explicit construction.

### Replicability argument

Let \(R(S)\) be the maximum cyclic distance from the target to an element of the version space. Nesting gives

\[
\Pr[R(S)\ge t]
\le
2\left(1-\frac{2t}{k}\right)^n
\le 2e^{-2nt/k}.
\]

Summing the tail yields

\[
\mathbb E R(S)
\le
\frac{2}{e^{2n/k}-1}
\le \frac{k}{n}.
\]

The union of the shortest paths from the target to the version space contains at most \(2R(S)\) cycle edges. Since a uniformly shifted partition with \(q\) blocks cuts each fixed edge with probability \(q/k\),

\[
\Pr[V(S)\text{ crosses a block boundary}]
\le
\frac{2q}{k}\mathbb E R(S)
\le \frac{2q}{n}.
\]

For two independent samples sharing the same shifted partition, if neither version space crosses a boundary then both runs output the representative of the same block containing the target. A union bound therefore gives mismatch probability at most \(4q/n\).

This is sufficient for the exact equality notion of replicability in the problem.

### Minor technical observations

- The proof works even when blocks have unequal sizes; a uniform cyclic shift still makes each edge a boundary with probability \(q/k\).
- Because \(X=\mathbb Z_k\) is finite, the output classifiers form a finite set, so no issue arises from improper output in the later mode argument.
- Standard measurability of the randomized learner is tacitly assumed, as is customary.

---

## Finding 2: A matching \( \Omega(1/(\varepsilon\rho)) \) lower bound holds for the fixed uniform distribution

**Claim key:** `uniform-cyclic-half-interval-replicable-lower-bound`

**Judgment:** Proven in the stated regime, including against randomized, computationally unbounded, improper learners.

The lower-bound statement has the correct order of quantifiers: a learner that works for every target \(h_i\) under the already fixed uniform distribution must have

\[
n\ge \frac{1}{120\varepsilon\rho}
\]

provided

\[
0<\varepsilon\le\frac14,\qquad
0<\delta,\rho\le\frac1{20},\qquad
k\ge\frac{1}{5\varepsilon\rho}.
\]

### Modes extracted from replicability

For fixed target \(i\) and seed \(r\), let \(\mu_{i,r}\) be the output distribution over the sample and let

\[
p_{i,r}=\max_f\mu_{i,r}(f).
\]

The fixed-seed collision probability is

\[
c_{i,r}=\sum_f\mu_{i,r}(f)^2.
\]

Since \(c_{i,r}\le p_{i,r}\), replicability implies

\[
\mathbb E_r[1-p_{i,r}]
\le \rho.
\]

This is a correct conversion from average collision probability to concentration on a mode.

If the chosen mode \(m_r(i)\) has error greater than \(\varepsilon\), then the fixed-seed probability of bad output is at least \(p_{i,r}\). Hence

\[
\mathbf 1\{\operatorname{err}_i(m_r(i))>\varepsilon\}
\le
a_{i,r}+1-p_{i,r},
\]

where \(a_{i,r}\) is the fixed-seed bad-output probability. Averaging gives

\[
\Pr_{i,r}[\operatorname{err}_i(m_r(i))>\varepsilon]
\le \delta+\rho.
\]

Importantly, this is only an average over targets and seeds; the later proof uses it only in that averaged form. No unjustified selection of a single favorable seed occurs.

### Symmetric coupling

For \(1\le n<k/24\), the proof defines

\[
M=\left\lfloor\frac{k}{12n}\right\rfloor.
\]

The bounds

\[
\frac{k}{24n}\le M\le \frac{k}{12n}\le\frac{k}{12}
\]

are valid. The first follows from \(k/(12n)>2\) and \(\lfloor x\rfloor\ge x/2\) for \(x\ge2\).

Targets \(i\) and \(i+M\) produce identical labels on a uniform sample with probability

\[
\alpha=\left(1-\frac{2M}{k}\right)^n
\ge 1-\frac{2nM}{k}
\ge \frac56.
\]

The sample-dependent kernel \(K_S\) moves from \(i\) to \(i+M\) or \(i-M\) only when the corresponding labeled samples are identical. Its off-diagonal coefficient

\[
\gamma=\frac{1}{3\alpha}
\]

satisfies \(2\gamma\le4/5\), so the diagonal entry is nonnegative. The kernel is symmetric and row-stochastic, hence doubly stochastic.

This establishes the crucial marginal facts:

- \((i,S)\) has the uniform-target/product-sample marginal;
- \((v,S)\) has the same correct marginal because \(K_S\) is doubly stochastic;
- whenever the coupling assigns positive probability, the two labeled inputs are identical;
- after averaging over \(S\), \(v-i\) is uniform on \(\{-M,0,M\}\).

These statements are enough to compare modes without feeding either learner a sample from the wrong target distribution.

### Replicability forces adjacent modes to agree

For a shared seed, identical labeled inputs give the same output. If the two target modes differ, that common output cannot equal both modes. Therefore

\[
\mathbf1\{m_r(i)\ne m_r(v)\}
\le
\mathbf1\{A(T_i(S);r)\ne m_r(i)\}
+
\mathbf1\{A(T_v(S);r)\ne m_r(v)\}.
\]

Each term averages to at most \(\rho\), using the two correct target/sample marginals. Thus

\[
\Pr[m_r(i)\ne m_r(v)]\le2\rho.
\]

If

\[
b=\Pr_{i,r}[m_r(i)\ne m_r(i+M)],
\]

translation invariance of the uniform target index gives the same probability for the \(-M\) edge. Since the coupling chooses each of \(-M,0,M\) with probability \(1/3\),

\[
\frac{2b}{3}\le2\rho,
\qquad
b\le3\rho.
\]

This is the central lower-bound consequence of replicability.

### Accuracy forces a change along a long path

Set

\[
t=\left\lfloor\frac{\varepsilon k}{M}\right\rfloor+1.
\]

Then

\[
\varepsilon k<tM\le\varepsilon k+M<\frac{k}{2}.
\]

Thus the endpoint targets \(h_i\) and \(h_{i+tM}\) disagree on mass

\[
\frac{2tM}{k}>2\varepsilon.
\]

A single classifier cannot be within error \(\varepsilon\) of both endpoints, by the triangle inequality for disagreement probability. Therefore, for every \(i,r\), either an endpoint mode is inaccurate or at least one of the \(t\) intervening mode edges changes.

Averaging this deterministic alternative gives

\[
1\le2(\delta+\rho)+tb.
\]

The estimate \(M\ge k/(24n)\) gives

\[
t\le24\varepsilon n+1.
\]

Combining this with \(b\le3\rho\) yields

\[
n\ge
\frac{1-2\delta-5\rho}{72\varepsilon\rho}.
\]

Under \(\delta,\rho\le1/20\), the numerator is at least \(13/20>72/120\), giving

\[
n\ge\frac{1}{120\varepsilon\rho}.
\]

The separate case \(n\ge k/24\) also gives the desired bound from \(k\ge1/(5\varepsilon\rho)\). The zero-sample case is correctly excluded using two targets whose \(\varepsilon\)-accuracy sets are disjoint.

No missing lemma is apparent in this lower-bound proof.

---

## Finding 3: The exact parameter-dependent “matching” conclusion needs a confidence qualification

**Claim key:** `uniform-cyclic-half-interval-sample-complexity-characterization`

**Judgment:** Correct for fixed small confidence parameters, but overstated if \(\delta\) is allowed to vary arbitrarily.

The proven bounds are

\[
n_{\mathrm{unif}}
\ge
\frac{1}{120\varepsilon\rho}
\]

and

\[
n_{\mathrm{unif}}
\le
\max\left\{
\frac1\varepsilon\log\frac2\delta,\,
\frac{12}{\varepsilon\rho}
\right\}.
\]

Therefore the supplied evidence establishes

\[
n_{\mathrm{unif}}
=
\Theta\!\left(\frac{1}{\varepsilon\rho}\right)
\]

when, for example:

- \(\delta\) and \(\rho\) are fixed sufficiently small constants; or
- more generally,
  \[
  \log(2/\delta)=O(1/\rho).
  \]

It does **not** establish this characterization uniformly over all
\(\delta,\rho\le1/20\). If \(\delta\) is extremely small relative to \(\rho\), the proved upper bound is governed by

\[
\frac{1}{\varepsilon}\log\frac1\delta,
\]

and no matching confidence-dependent lower bound is supplied.

Accordingly, the sentence asserting \(\Theta(1/(\varepsilon\rho))\) “in the lower-bound regime” should explicitly say that \(\delta,\rho\) are fixed, or impose an appropriate relation between them. This issue does not affect either numbered theorem statement.

---

## Finding 4: The transfer to the worst-case quantity \(n_{\mathrm{rep}}\) is valid, but weak

**Claim key:** `worst-case-replicable-lower-bound-from-uniform-half-intervals`

**Judgment:** Valid under the stated odd-\(k\) and parameter conditions.

A learner counted by \(n_{\mathrm{rep}}(k,\varepsilon,\delta,\rho)\) must work for every distribution on the chosen domain. In particular, it must work for the uniform distribution on \(\mathbb Z_k\) and every target in \(H_k\). Therefore the restricted lower bound implies

\[
n_{\mathrm{rep}}(k,\varepsilon,\delta,\rho)
\ge
\frac{1}{120\varepsilon\rho}.
\]

This transfer is logically correct even though the restricted upper bound does not transfer.

The corollary has no growing \(\log k\) factor and consequently does not improve the established headline lower bound. It is best understood as validating the local one-coordinate obstruction rather than advancing the worst-case exponent.

---

## Finding 5: The negative conclusion about alphabet size is valid only for the uniform-distribution mechanism

**Claim key:** `absence-of-log-k-cost-for-uniform-one-coordinate-half-intervals`

**Judgment:** Supported in the restricted setting; unsupported if read as a claim about all distributions on \(H_k\).

The proper learner has a sample bound independent of \(k\) once \(\varepsilon,\delta,\rho\) are fixed. Thus increasing \(k=|H_k|\) cannot create an additional \(\log k\) cost for learning this class under the fixed uniform distribution.

However, the contribution proves no learner for arbitrary distributions \(D\) on \(\mathbb Z_k\). Consequently, it does not exclude the possibility that the same hypothesis class \(H_k\), paired with a nonuniform adversarial distribution, has larger worst-case replicable sample complexity.

The strongest warranted interpretation is therefore:

> The uniform one-coordinate component of the cyclic half-interval construction does not by itself generate a growing \(\log k\) factor.

A broader claim that the hypothesis family \(H_k\) can never support such a lower bound would require an arbitrary-distribution learner or another hardness classification, neither of which is supplied.

---

## Finding 6: The coordinatewise tensorization discussion is correctly labeled as heuristic

**Claim key:** `naive-coordinatewise-replicability-tensorization-scaling`

**Judgment:** Plausible scaling observation, not a theorem about the original multidimensional i.i.d. family.

If \(d\) coordinates each receive approximately \(n/d\) samples, applying the one-coordinate boundary estimate suggests a per-coordinate instability of order

\[
\frac{d}{n\varepsilon}.
\]

A union bound over \(d\) coordinates then suggests total mismatch of order

\[
\frac{d^2}{n\varepsilon},
\]

and hence the naive requirement

\[
n=O\!\left(\frac{d^2}{\varepsilon\rho}\right).
\]

The contribution expressly acknowledges that the original i.i.d. multidimensional sample does not provide a deterministic \(n/d\) samples to every coordinate and that a global learner may exploit more structure. No theorem for the \(d\)-coordinate construction follows from this calculation. The disclaimer is appropriate.

---

## Relation to the original open problem

The contribution does not provide any of the following:

- a lower bound with \((\log |H|)^c\) for \(c>3/2\);
- a universal learner with exponent \(c<2\);
- an arbitrary-distribution learner for
