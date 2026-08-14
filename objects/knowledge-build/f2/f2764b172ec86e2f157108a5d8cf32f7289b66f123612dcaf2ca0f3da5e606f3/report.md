# Knowledge-Formation Report

This build establishes one durable research program for the Freund–Karloff midpoint family while preserving the central exact-value question and the current unconditional bounds as global root-level knowledge. No conflict records or reconciliation outcomes were supplied, so no active dispute node is required.

## Node: root

- **Type:** Root
- **Status:** Active
- **Title:** Research state for the integrality gap of the CKR relaxation for Multiway Cut

The governed quantity is

\[
\Gamma=\sup_{k\ge 3}\Gamma_k,
\qquad
\Gamma_k=
\sup_{\substack{(G,T,w):\,|T|=k\\ \operatorname{CKR}(G,T,w)>0}}
\frac{\operatorname{OPT}(G,T,w)}
{\operatorname{CKR}(G,T,w)}.
\]

Its exact value remains unresolved in the supplied knowledge state. The current unconditional bracket remains

\[
1.20016\le \Gamma\le 1.2787.
\]

The lower endpoint is established background obtained through an auxiliary non-opposite-cut problem on \(\Delta_4\) and a transfer to conventional instances with a growing number of terminals; it is not a four-terminal CKR gap. The upper endpoint is established background from a rigorously interval-certified rounding scheme.

One durable program is currently represented:

1. `programs/freund-karloff-midpoint` — exact construction, optimization certificates, finite verification, and classical lower bounds for the Freund–Karloff midpoint family.

According to judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`, that family gives

\[
\Gamma_k\ge \frac{8(k-1)}{7k-6}
\quad\text{and}\quad
\Gamma\ge\frac87,
\]

including a four-terminal ratio \(12/11\). These are valid exact baseline bounds but are weaker than \(1.20016\), so they do not change the global bracket. The judgment also finds no universal CKR rounding argument or improved upper bound in the supporting transaction.

There are no supplied conflict records, incompatible judgments, or reconciliation outcomes requiring an active dispute node.

**Provenance**

- Governed problem statement and its stated frontier background, checked against the listed primary sources on 2026-08-12.
- Primary judgment: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`, ledger position 1.

## Change: root

The previous root stated that no research programs existed. This build replaces that empty organizational state with the global exact-value question, the unchanged unconditional bracket, and the newly established Freund–Karloff midpoint-family program. The bracket is preserved rather than revised because the primary judgment expressly finds that the certified ratios do not improve either governed endpoint.

## Node: global/exact-value-question

- **Type:** Question
- **Parent:** `root`
- **Status:** Open
- **Title:** Exact integrality gap of the CKR relaxation

The central cross-program question is to determine the exact value of

\[
\Gamma=\sup_{k\ge3}\Gamma_k
\]

for the CKR relaxation of conventional finite Multiway Cut instances.

Within the supplied state, this question remains open. A frontier advance would require either:

\[
\Gamma\ge L\quad\text{for an explicit }L>1.20016,
\]

with the permitted finite-instance or fully transferred asymptotic certification, or

\[
\Gamma\le U\quad\text{for an explicit }U<1.2787,
\]

through a universal comparison against the CKR value of every finite instance.

Primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` does not resolve this question. It classifies the Freund–Karloff midpoint family as a correct baseline whose limiting ratio \(8/7\) is below the governed lower benchmark and which supplies no universal upper-bound argument.

**Provenance**

- Governed problem statement.
- Primary judgment: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: global/exact-value-question

This node is created to preserve the central unresolved question directly under the root rather than placing it inside the newly formed midpoint-family program. The judgment’s explicit finding of no frontier improvement confirms that the question remains open.

## Node: global/current-unconditional-bracket

- **Type:** Result
- **Parent:** `root`
- **Status:** Active
- **Title:** Current unconditional bounds on the CKR integrality gap

The current unconditional bounds are

\[
1.20016\le \Gamma\le1.2787.
\]

The lower benchmark comes from an auxiliary non-opposite-cut problem on \(\Delta_4\) together with a transfer to conventional Multiway Cut instances having a growing number of terminals. It is not a four-terminal CKR integrality gap. The upper benchmark comes from a rigorously interval-certified rounding scheme. These benchmark facts are supplied frontier background rather than evidence originating in the supporting ledger transaction.

Primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` leaves both endpoints unchanged:

- the certified four-terminal midpoint instance has ratio
  \[
  \frac{12}{11}<1.20016;
  \]
- the complete midpoint family has supremal ratio
  \[
  \frac87<1.20016;
  \]
- no rounding distribution or universal comparison proving an upper bound below \(1.2787\) is supplied.

Thus the midpoint-family results are compatible with, but do not strengthen, the current bracket.

**Provenance**

- Governed problem statement and listed frontier sources.
- Primary judgment, especially Finding 5: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: global/current-unconditional-bracket

This node is created as a global result because the best known lower and upper bounds span all research programs. Its values are not changed: the primary judgment expressly refutes the claim that the supporting midpoint-family material improves the governed bracket.

## Node: programs/freund-karloff-midpoint

- **Type:** Program
- **Parent:** `root`
- **Status:** Active
- **Title:** Freund–Karloff midpoint-family exact baseline

This program organizes the exact construction and certification of the conventional Freund–Karloff midpoint family \(H_k\), for every integer \(k\ge3\). Its durable scope includes:

- the rationally weighted graph family;
- the exact CKR optimum and its convex subgradient certificate;
- the local finite cut lemma and the resulting exact integral optimum;
- the explicit four-terminal specialization \(H_4\);
- the family’s exact integrality ratios and classical asymptotic lower bound.

According to primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`, the family satisfies

\[
\operatorname{CKR}(H_k)=\frac{7k-6}{8(k-1)},
\qquad
\operatorname{OPT}(H_k)=1,
\]

and hence has ratio

\[
\frac{8(k-1)}{7k-6}\longrightarrow\frac87.
\]

The program is an exact baseline and regression resource, not a frontier improvement: its supremal ratio is below \(1.20016\), and it supplies no upper bound below \(1.2787\).

The judgment carries forward attribution of the mathematical family and ratio formula to **Ari Freund and Howard Karloff**. It identifies the supporting transaction’s added work as the explicit \(k=4\) rational instance, compact exact subgradient presentation, normalization audit, and standard-library verifier; it does not credit that transaction with discovery of the original family.

**Children**

- `programs/freund-karloff-midpoint/construction`
- `programs/freund-karloff-midpoint/ckr-optimum`
- `programs/freund-karloff-midpoint/integral-optimum`
  - `programs/freund-karloff-midpoint/integral-optimum/local-cut-lemma`
- `programs/freund-karloff-midpoint/h4-exact-instance`
- `programs/freund-karloff-midpoint/integrality-ratios`

**Provenance**

- Primary judgment: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint

This program is created because the judgment validates a coherent, long-lived mathematical agenda centered on one parameterized graph family, its exact optima, and reusable certificates. It is not named after the supporting transaction and remains meaningful independently of submission chronology.

## Node: programs/freund-karloff-midpoint/construction

- **Type:** Construction
- **Parent:** `programs/freund-karloff-midpoint`
- **Status:** Established
- **Title:** Rational midpoint graph family \(H_k\)

For every integer \(k\ge3\), the Freund–Karloff midpoint graph \(H_k\) is a conventional \(k\)-terminal Multiway Cut instance with terminals

\[
t_1,\ldots,t_k
\]

and one nonterminal \(m_{ij}\) for each unordered pair \(\{i,j\}\subseteq[k]\).

Its edges and weights are:

1. **Outer edges.** For every pair \(i<j\), the two edges
   \[
   \{t_i,m_{ij}\},\qquad \{t_j,m_{ij}\}
   \]
   each have weight
   \[
   a=\frac1{(k-1)^2}.
   \]

2. **Inner edges.** For every triple \(\{i,j,\ell\}\), the three midpoint vertices
   \[
   m_{ij},\quad m_{i\ell},\quad m_{j\ell}
   \]
   form a triangle. Each of its three edges has weight
   \[
   b=\frac{3}{2k(k-1)^2}.
   \]

Consequently, \(H_k\) has

\[
k+\binom{k}{2}
\]

vertices,

\[
k(k-1)
\]

outer edges, and

\[
3\binom{k}{3}
\]

inner edges.

Primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` finds that these weights agree exactly with the normalization arising from the integral averaging certificate and with the CKR objective calculation. No internal inconsistency was found among the symbolic family, the \(k=4\) specialization, and the exact verifier.

The mathematical family is attributed, as carried forward by the judgment, to Ari Freund and Howard Karloff.

**Provenance**

- Primary judgment, Findings 1–4: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint/construction

This node is created to give the program’s graph family a stable mathematical identity independent of its optimum calculations. The judgment verifies that the rational weights, edge types, normalization, and finite specialization are mutually consistent.

## Node: programs/freund-karloff-midpoint/ckr-optimum

- **Type:** Result
- **Parent:** `programs/freund-karloff-midpoint`
- **Status:** Established
- **Title:** Exact CKR value of the midpoint family

For every integer \(k\ge3\), primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` certifies

\[
\operatorname{CKR}(H_k)=\frac{7k-6}{8(k-1)}.
\]

The certified feasible embedding is

\[
x_{t_i}=e_i,
\qquad
x_{m_{ij}}=\frac{e_i+e_j}{2}.
\]

Every outer and inner edge in \(H_k\) has half-\(\ell_1\) length \(1/2\) under this embedding. With \(k(k-1)\) outer edges and \(3\binom{k}{3}\) inner edges, its objective value is

\[
\frac12\left(k(k-1)a+3\binom{k}{3}b\right)
=
\frac{7k-6}{8(k-1)}.
\]

The judgment also validates the matching convex optimality certificate. At every midpoint \(m_{ij}\), suitable exact choices at zero absolute-value differences make the objective subgradient the constant vector

\[
\mu\mathbf 1,
\qquad
\mu=\frac{3(k-2)}{4k(k-1)^2}.
\]

For every other feasible simplex point, the coordinate differences at a midpoint sum to zero. The subgradient inequality therefore gives no negative first-order term and proves that the displayed feasible embedding is globally optimal.

The judgment explicitly finds this argument valid even though the midpoint vectors lie on the boundary of the simplex: the selected vectors are genuine subgradients of the unrestricted convex objective, and the comparison is restricted to feasible simplex embeddings.

**Confidence recorded by the judgment:** High.

**Certificate scope**

The exact verifier supplied through the evidence transaction checks the same stationarity calculation using rational arithmetic for the committed \(k=4\) instance. The judgment notes that the script is intentionally not a machine certificate for arbitrary \(k\); the all-\(k\) result rests on the validated symbolic argument.

**Provenance**

- Primary judgment, Finding 1: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint/ckr-optimum

This node is created because the primary judgment validates a distinct exact optimization result for the entire parameterized family, including both feasibility and a matching convex subgradient certificate. The verifier’s finite scope is retained as a provenance qualification rather than extended to arbitrary \(k\).

## Node: programs/freund-karloff-midpoint/integral-optimum

- **Type:** Result
- **Parent:** `programs/freund-karloff-midpoint`
- **Status:** Established
- **Title:** Exact integral optimum of the midpoint family

For every integer \(k\ge3\), primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` certifies

\[
\operatorname{OPT}(H_k)=1.
\]

The certified lower bound uses two normalized weightings:

- \(W\), the average over all terminal triples of the local weighting recorded in `programs/freund-karloff-midpoint/integral-optimum/local-cut-lemma`;
- \(W'\), which gives every terminal–midpoint edge weight \(1/\binom{k}{2}\).

For an integral labeling \(f\), let

\[
q=\#\{m_{ij}:f(m_{ij})\notin\{i,j\}\}.
\]

The judgment validates the bounds

\[
C_W(f)\ge 1-\frac{q}{3\binom{k}{3}}
\]

and

\[
C_{W'}(f)=1+\frac{q}{\binom{k}{2}}.
\]

In the convex combination

\[
\frac{k-2}{k-1}W+\frac1{k-1}W',
\]

the coefficients of \(q\) cancel exactly. The resulting outer- and inner-edge weights are respectively

\[
\frac1{(k-1)^2}=a
\quad\text{and}\quad
\frac{3}{2k(k-1)^2}=b,
\]

so the combination is precisely the weighting of \(H_k\). Every integral labeling therefore costs at least \(1\).

The judgment also validates a matching labeling: assign \(m_{ij}\) the label \(i\) whenever \(i<j\). This cuts one outer edge per pair and two inner edges per terminal triple, with total cost

\[
\binom{k}{2}a+2\binom{k}{3}b=1.
\]

Thus the lower bound is attained.

**Confidence recorded by the judgment:** High.

**Provenance**

- Primary judgment, Finding 2: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint/integral-optimum

This node is created because the judgment validates a distinct exact integral optimization theorem for all \(k\ge3\). Its current statement incorporates the local-lemma dependency, the averaging normalization, the cancellation argument, and the attaining labeling certified by the judgment.

## Node: programs/freund-karloff-midpoint/integral-optimum/local-cut-lemma

- **Type:** Lemma
- **Parent:** `programs/freund-karloff-midpoint/integral-optimum`
- **Status:** Established
- **Title:** Three-midpoint local cut bounds

Consider three selected terminals and the associated three pair-midpoint vertices. Give each of the six terminal–midpoint edges weight \(1/6\) and each of the three edges among the pair midpoints weight \(1/4\).

Primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` certifies the following exact statements for assignments of the three midpoint labels from four available labels:

1. Every labeling has local cut cost at least
   \[
   \frac23.
   \]

2. Every non-opposite labeling has local cut cost at least
   \[
   1.
   \]

Here the non-opposite restriction excludes assigning a midpoint \(m_{ij}\) the third selected terminal’s label; endpoint labels and the fourth, collapsed outside label remain permitted.

The evidence verifier exhausts all

\[
4^3=64
\]

assignments using exact rational arithmetic and separately filters the non-opposite assignments. The judgment finds that this enumeration covers exactly the claimed finite domain and uses no floating-point comparisons.

In the global averaging argument, a pair midpoint whose label lies outside its endpoint pair can make at most one selected terminal triple fail the non-opposite condition. This is the certified local fact supporting the bound

\[
C_W(f)\ge1-\frac{q}{3\binom{k}{3}}.
\]

**Confidence recorded by the judgment:** High.

**Provenance**

- Primary judgment, Finding 2 and its local-lemma analysis: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint/integral-optimum/local-cut-lemma

This node is created because the finite local inequalities are a durable mathematical dependency of the family-wide integral lower bound. The judgment independently validates their exact exhaustive certificate and their role in controlling bad terminal triples.

## Node: programs/freund-karloff-midpoint/h4-exact-instance

- **Type:** Exact finite instance
- **Parent:** `programs/freund-karloff-midpoint`
- **Status:** Established
- **Title:** Four-terminal midpoint instance \(H_4\)

The \(k=4\) specialization of the Freund–Karloff midpoint family is a conventional finite Multiway Cut instance with:

- \(4\) terminals;
- \(\binom42=6\) midpoint nonterminals;
- \(10\) vertices in total;
- \(12\) outer edges, each of weight
  \[
  a=\frac19;
  \]
- \(12\) inner edges, each of weight
  \[
  b=\frac1{24};
  \]
- \(24\) edges in total.

Primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` certifies the exact values

\[
\operatorname{CKR}(H_4)=\frac{11}{12},
\qquad
\operatorname{OPT}(H_4)=1,
\]

and therefore

\[
\frac{\operatorname{OPT}(H_4)}
{\operatorname{CKR}(H_4)}
=\frac{12}{11}.
\]

The exact-arithmetic verifier exhausts all

\[
4^6=4096
\]

assignments of the six nonterminals. The judgment regards this as an independent finite-instance check in addition to the general symbolic proof. It also reports \(28\) minimizing assignments, consistent with \(24\) endpoint-label minimizers corresponding to transitive orientations of \(K_4\) and \(4\) constant-label minimizers.

This finite instance does not establish a ratio of \(1.20016\) for four terminals. Its certified ratio is only

\[
\frac{12}{11}\approx1.09091.
\]

The judgment identifies the explicit rational \(H_4\) data and its standard-library verifier as reconstruction and verification work supplied by transaction `ab06d88e87e635c3bbb8967fedafe51b26238ec9`, without attributing discovery of the underlying family to that transaction.

**Confidence recorded by the judgment:** High.

**Provenance**

- Primary judgment, Finding 3 and contribution assessment: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint/h4-exact-instance

This node is created because the four-terminal specialization is a distinct durable finite certificate with explicit rational weights, exact objective values, and complete assignment enumeration. It is kept separate from the asymptotic family bound to preserve the judgment’s distinction between the \(12/11\) four-terminal gap and the \(8/7\) limit.

## Node: programs/freund-karloff-midpoint/integrality-ratios

- **Type:** Result
- **Parent:** `programs/freund-karloff-midpoint`
- **Status:** Established baseline
- **Title:** Integrality ratios furnished by the midpoint family

Combining the exact values certified by primary judgment `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07` gives, for every \(k\ge3\),

\[
\frac{\operatorname{OPT}(H_k)}
{\operatorname{CKR}(H_k)}
=
\frac{8(k-1)}{7k-6}
=
\frac{8}{7+1/(k-1)}.
\]

Because each \(H_k\) is a finite conventional \(k\)-terminal instance, the family proves

\[
\Gamma_k\ge\frac{8(k-1)}{7k-6}.
\]

As \(k\) grows,

\[
\frac{8(k-1)}{7k-6}\longrightarrow\frac87,
\]

so the family also proves the classical lower bound

\[
\Gamma\ge\frac87.
\]

The judgment classifies these conclusions as exact and valid but not frontier-improving:

\[
\frac87\approx1.142857<1.20016.
\]

Likewise, the four-terminal specialization yields only

\[
\Gamma_4\ge\frac{12}{11}.
\]

The local use of four labels in the supporting non-opposite-cut lemma does not convert the limiting \(8/7\) result into a four-terminal CKR gap. The judgment expressly preserves this distinction.

No upper bound follows from this family: the judgment finds no rounding distribution or universal expected-cost comparison against the CKR value.

**Confidence recorded by the judgment:** High for the ratio formula and resulting classical lower bounds.

**Credit**

The judgment carries forward attribution of the family and ratio formula to Ari Freund and Howard Karloff. The supporting transaction is credited only with reconstruction and verification work identified in the program and \(H_4\) nodes.

**Provenance**

- Primary judgment, Findings 4 and 5: `sha256:23d8efa092943fae2b782a0804f04f8e78142612a3553f56806b14a7a6762f07`.
- Subject and evidence transaction: `ab06d88e87e635c3bbb8967fedafe51b26238ec9`.

## Change: programs/freund-karloff-midpoint/integrality-ratios

This node is created to record the durable lower bounds obtained from the family’s exact optima while retaining their judged scope. It records both the valid \(k\)-dependent and asymptotic bounds and the explicit finding that neither improves the governed lower benchmark or supplies an upper-bound result.
