# Knowledge-Formation Report

This build establishes one durable research program for prescribed finite families of trace-normalized rank-one metrics. It preserves the full Gaussian metric-universality problem, its definition-immediate bracket, and its unresolved status at root level.

No conflict records or reconciliation outcomes were supplied. The unresolved full minimax question is therefore represented as an open question, not as an adjudicative dispute.

Proposed hierarchy:

```text
root
└── program/finite-rank-one-families
    ├── program/finite-rank-one-families/simultaneous-nonorthogonality
    ├── program/finite-rank-one-families/collinear-quantization
    └── program/finite-rank-one-families/restricted-overhead-bound
        └── program/finite-rank-one-families/subexponential-zero-overhead
            └── program/finite-rank-one-families/subexponential-witness-limitation
```

## Node: root

- **Type:** Root
- **Title:** Research state for metric-universality-price
- **Status:** Active
- **Parent:** None

### Global question

For the minimax overhead

\[
\pi(R)=\liminf_{n\to\infty}
\inf_{\substack{C\subset\mathbb R^n\\|C|=\lceil2^{nR}\rceil}}
\sup_{\substack{\Sigma\succeq0\\\operatorname{tr}\Sigma=n}}
\left[
\frac1n\log_2\lceil2^{nR}\rceil
-
R_{\mathrm{wf}}\bigl(\Sigma,D(C,\Sigma)\bigr)
\right],
\]

the central question remains whether there exist \(R_0>0\) and \(\delta>0\) such that

\[
\pi(R_0)\geq\delta,
\]

or instead whether universal codebooks can establish

\[
\pi(R)=0
\qquad\text{for every fixed }R>0.
\]

The immutable primary judgment does not decide between these alternatives.

### Current certified global bounds

For the full deterministic worst-case class of all positive-semidefinite trace-\(n\) metrics, the supplied judgment leaves the definition-immediate bracket unchanged:

\[
0\leq \pi(R)\leq R.
\]

The newly established restricted rank-one-family result gives neither:

- a positive lower bound for the full \(\pi(R)\), nor
- a smaller upper bound for the full \(\pi(R)\).

Its codebooks may depend on a prescribed finite orientation family and have no established control over all rank-one orientations or over higher-rank metrics.

### Durable research programs

One program is active:

- [`program/finite-rank-one-families`](#node-programfinite-rank-one-families): restricted minimax quantization for prescribed finite families of trace-normalized rank-one metrics, including collinear codebooks and limitations on subexponential finite-family lower-bound strategies.

### Conflict status

No conflict records were supplied. There is consequently no active adjudicative dispute node in the current state. The full minimax question remains open because the judgment records insufficient evidence to resolve it, not because opposed judgments require reconciliation.

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Relevant judgment finding:** `strict-cost-of-full-gaussian-metric-universality`

## Change: root

The root previously reported no established programs. This build adds the finite-rank-one-family program while retaining the unresolved full minimax question and the unchanged global bracket \(0\leq\pi(R)\leq R\), exactly as qualified by the primary judgment.

## Node: program/finite-rank-one-families

- **Type:** Research program
- **Title:** Prescribed finite families of trace-normalized rank-one metrics
- **Status:** Active
- **Parent:** `root`

### Program scope

This program studies restricted minimax overhead when the uncertainty set is a prescribed finite family

\[
\mathcal U=\{u_1,\ldots,u_m\}\subset S^{n-1}
\]

of orientations, with corresponding metrics

\[
\Sigma_u=n uu^{\mathsf T}.
\]

The codebook may be tailored to the entire prescribed family \(\mathcal U\), but must work simultaneously for every metric in that family.

For \(M\) codewords, the restricted minimax functional is

\[
\Pi_n(\mathcal U,M)
=
\inf_{\substack{C\subset\mathbb R^n\\|C|=M}}
\max_{u\in\mathcal U}
\left[
\frac{\log_2M}{n}
-
R_{\mathrm{wf}}
\bigl(nuu^{\mathsf T},D(C,nuu^{\mathsf T})\bigr)
\right].
\]

According to the primary judgment, the program currently establishes:

1. an existential vector simultaneously nonorthogonal to every orientation in an arbitrary finite family, with quantitative projection bounds;
2. a collinear \(M\)-word codebook with a uniform scalar-quantization distortion bound over the family;
3. a finite-dimensional restricted-overhead upper bound whenever that distortion bound is below one;
4. convergence
   \[
   \Pi_n(\mathcal U_n,M_n)\to0
   \]
   for fixed positive rate and prescribed subexponential-size orientation families;
5. the resulting limitation that a prescribed subexponential family of rank-one orientations cannot itself witness a positive asymptotic universality price against every codebook.

### Program boundary

The judgment expressly limits these conclusions to prescribed finite rank-one families. They do not control:

- exponentially large orientation families;
- the continuum of all rank-one orientations;
- adversarial families selected in a genuinely codebook-dependent way from a larger class;
- higher-rank or full-rank metrics; or
- the full trace-\(n\) positive-semidefinite minimax problem.

The collinear codebook may perform poorly outside its selected family. In particular, an orientation orthogonal to its codebook line can give all codewords identical scalar projections. No covering, continuity, or approximation theorem has been supplied to pass from the restricted family to the full metric class.

### Construction status

The codebook has an explicit formula after a suitable direction vector is supplied. The direction vector itself is obtained only by the probabilistic method. The program therefore establishes an existence result, not a deterministic efficient construction with complexity or finite-precision guarantees.

### Credit and priority provenance

The primary judgment reports that the underlying artifact attributes the proof and exposition to its named contributor and an OpenAI Codex research agent. It also records that no independent literature search or external priority evidence was supplied. The current organization carries that credit statement forward without independently reassessing novelty or priority.

### Child nodes

- `program/finite-rank-one-families/simultaneous-nonorthogonality`
- `program/finite-rank-one-families/collinear-quantization`
- `program/finite-rank-one-families/restricted-overhead-bound`

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Relevant judgment findings:** all six routed findings concerning finite rank-one families and the unresolved full problem

## Change: program/finite-rank-one-families

This new program is warranted because the judgment validates a coherent, long-lived restricted agenda concerning prescribed finite rank-one metric families. The program remains meaningful independently of the originating transaction and is kept separate from the unresolved full positive-semidefinite minimax problem.

## Node: program/finite-rank-one-families/simultaneous-nonorthogonality

- **Type:** Lemma
- **Title:** Simultaneous quantitative nonorthogonality for finite orientation families
- **Status:** Supported
- **Parent:** `program/finite-rank-one-families`

For every arbitrary finite family

\[
u_1,\ldots,u_m\in S^{n-1},
\]

the primary judgment assesses the supplied probabilistic argument as proving the existence of a vector \(v\in\mathbb R^n\) such that

\[
\frac1{4m}\leq |u_i^{\mathsf T}v|
\leq \sqrt{2\ln(8m)}
\qquad\text{for every }i.
\]

Writing

\[
\alpha_i=u_i^{\mathsf T}v,
\qquad
\alpha_*=\min_i|\alpha_i|,
\]

the same result gives

\[
\frac{\max_i|\alpha_i|}{\alpha_*}
\leq
4m\sqrt{2\ln(8m)}
=:\beta_m.
\]

The judgment records that this existence statement is uniform over arbitrary geometry of the family: the orientations may be repeated, linearly dependent, highly clustered, or otherwise dependent. Independence among the random Gaussian projections is not required by the supplied argument.

The result is existential. The judgment does not recognize any deterministic algorithm, complexity bound, numerical-stability guarantee, or finite-precision procedure for finding such a vector \(v\).

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Claim key:** `simultaneous-nonorthogonality-for-finite-unit-vector-families`
- **Judgment stance:** Supports

## Change: program/finite-rank-one-families/simultaneous-nonorthogonality

This new lemma node records the durable quantitative existence result validated by the primary judgment. Its algorithmic limitation is included in the same concept rather than materialized as an event-shaped correction or separate construction claim.

## Node: program/finite-rank-one-families/collinear-quantization

- **Type:** Construction and distortion theorem
- **Title:** Simultaneous collinear quantization for finite rank-one metric families
- **Status:** Supported with an explicitness qualification
- **Parent:** `program/finite-rank-one-families`

Let

\[
\mathcal U=\{u_1,\ldots,u_m\}\subset S^{n-1},
\qquad
\Sigma_i=n u_i u_i^{\mathsf T},
\]

and define

\[
\beta_m=4m\sqrt{2\ln(8m)}.
\]

According to the primary judgment, there exists a vector \(v\) with

\[
\alpha_i=u_i^{\mathsf T}v,\qquad
\alpha_*=\min_i|\alpha_i|>0,\qquad
\frac{\max_i|\alpha_i|}{\alpha_*}\leq\beta_m.
\]

For \(M\geq2\), set

\[
A=2\sqrt{\ln M}
\]

and define the collinear codebook

\[
C=\{c_1,\ldots,c_M\},\qquad c_j=s_jv,
\]

where

\[
s_j
=
-\frac{A}{\alpha_*}
+
\frac{2A(j-1)}{\alpha_*(M-1)}.
\]

The judgment assesses the construction as proving, simultaneously for all \(i\),

\[
D(C,\Sigma_i)\leq B(M,m),
\]

with

\[
B(M,m)=
\frac{4\beta_m^2\ln M}{(M-1)^2}
+
\frac{2}{\sqrt{2\pi}\,M^2}
\left(
2\sqrt{\ln M}
+
\frac{1}{2\sqrt{\ln M}}
\right).
\]

For metric \(i\), the projected codewords form an equally spaced scalar grid with endpoint magnitude

\[
L_i=A\frac{|\alpha_i|}{\alpha_*}\geq A
\]

and spacing

\[
h_i=\frac{2L_i}{M-1}
\leq\frac{2A\beta_m}{M-1}.
\]

The primary judgment validates the reduction

\[
D(C,\Sigma_i)
=
\mathbb E\min_{c\in C}
\bigl(Z-u_i^{\mathsf T}c\bigr)^2,
\qquad Z\sim N(0,1),
\]

so the normalized rank-one distortion is exactly the associated scalar mean-square quantization error. No extra factor of \(n\) is required.

### Explicitness qualification

The codeword formula is explicit after a suitable vector \(v\) is supplied. The judgment qualifies stronger algorithmic claims because \(v\) is established only existentially through a Gaussian probabilistic argument. The current result does not provide:

- a deterministic construction or search algorithm;
- a computational complexity bound;
- finite-precision guarantees; or
- a numerical-stability analysis.

Thus the construction is explicit only in the weak formulaic sense and is not established as an efficient explicit codebook construction.

### Scope

The guarantee applies only to the prescribed family \(\mathcal U\). It supplies no uniform distortion control for orientations outside that family and no control for general higher-rank metrics.

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Claim keys:**
  - `collinear-codebook-distortion-bound-for-finite-rank-one-metric-families`
  - `collinear-codebook-construction/algorithmic-explicitness`
- **Judgment stances:** Supports the distortion theorem; qualifies algorithmic explicitness

## Change: program/finite-rank-one-families/collinear-quantization

This new node consolidates the validated codebook formula, its simultaneous distortion guarantee, and the judgment’s explicitness qualification into one stable construction concept. No separate node is created for the qualification because it modifies the status of this construction rather than defining an independent mathematical result.

## Node: program/finite-rank-one-families/restricted-overhead-bound

- **Type:** Finite-dimensional minimax result
- **Title:** Restricted overhead bound for a finite rank-one family
- **Status:** Supported subject to the supplied Gaussian rate-distortion converse
- **Parent:** `program/finite-rank-one-families`

For a prescribed finite family

\[
\mathcal U=\{u_1,\ldots,u_m\}\subset S^{n-1},
\]

define

\[
\Pi_n(\mathcal U,M)
=
\inf_{\substack{C\subset\mathbb R^n\\|C|=M}}
\max_{u\in\mathcal U}
\left[
\frac{\log_2M}{n}
-
R_{\mathrm{wf}}
\bigl(nuu^{\mathsf T},D(C,nuu^{\mathsf T})\bigr)
\right].
\]

Let

\[
\beta_m=4m\sqrt{2\ln(8m)}
\]

and

\[
B(M,m)=
\frac{4\beta_m^2\ln M}{(M-1)^2}
+
\frac{2}{\sqrt{2\pi}\,M^2}
\left(
2\sqrt{\ln M}
+
\frac{1}{2\sqrt{\ln M}}
\right).
\]

Whenever

\[
B(M,m)<1,
\]

the primary judgment assesses the supplied argument as proving

\[
0\leq \Pi_n(\mathcal U,M)
\leq
\frac1{2n}\log_2\!\bigl(M^2B(M,m)\bigr).
\]

The lower bound is attributed to the Gaussian rate-distortion converse supplied with the problem.

For a rank-one metric

\[
\Sigma=n uu^{\mathsf T},
\]

whose spectrum is \((n,0,\ldots,0)\), the judgment validates the water-filling identity

\[
R_{\mathrm{wf}}(\Sigma,D)
=
\frac1{2n}\log_2\frac1D
\qquad (0<D<1).
\]

The collinear codebook has positive distortion and satisfies \(D\leq B(M,m)<1\), placing it in this water-filling regime. The distortion bound therefore yields the stated restricted-overhead upper bound.

This is a family-dependent restricted theorem. The optimizing codebook may depend on \(\mathcal U\), so the result does not provide an upper bound for the full minimax overhead \(\pi(R)\).

### Child node

- `program/finite-rank-one-families/subexponential-zero-overhead`

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Claim key:** `finite-rank-one-family-overhead-upper-bound`
- **Judgment stance:** Supports, assuming the supplied converse

## Change: program/finite-rank-one-families/restricted-overhead-bound

This new node records the durable finite-dimensional minimax consequence of the validated collinear distortion theorem. It is kept distinct from the construction because it introduces the restricted overhead functional, a water-filling conversion, and a conditional minimax bound.

## Node: program/finite-rank-one-families/subexponential-zero-overhead

- **Type:** Asymptotic theorem
- **Title:** Zero restricted minimax overhead for prescribed subexponential rank-one families
- **Status:** Supported
- **Parent:** `program/finite-rank-one-families/restricted-overhead-bound`

Fix \(R>0\) and let

\[
M_n=\lceil2^{nR}\rceil.
\]

For any prescribed sequence of finite orientation families

\[
\mathcal U_n\subset S^{n-1}
\]

satisfying

\[
\ln|\mathcal U_n|=o(n),
\]

the primary judgment assesses the supplied asymptotic estimates as proving

\[
\Pi_n(\mathcal U_n,M_n)\longrightarrow0.
\]

Writing \(m_n=|\mathcal U_n|\), the judgment specifically validates:

\[
B(M_n,m_n)=o(1),
\]

so \(B(M_n,m_n)<1\) for all sufficiently large \(n\), and

\[
\log_2\!\bigl(M_n^2B(M_n,m_n)\bigr)=o(n).
\]

Consequently, the finite-dimensional restricted bound gives

\[
0\leq
\Pi_n(\mathcal U_n,M_n)
\leq
\frac1{2n}
\log_2\!\bigl(M_n^2B(M_n,m_n)\bigr)
=o(1).
\]

The quantifier over \(\mathcal U_n\) permits arbitrary prescribed family geometry but requires subexponential cardinality. The family is fixed independently of the selected codebook, after which the codebook may be tailored to that family.

This theorem concerns only the restricted functional \(\Pi_n\). It does not establish \(\pi(R)=0\) for the full positive-semidefinite trace-\(n\) uncertainty class.

### Child node

- `program/finite-rank-one-families/subexponential-witness-limitation`

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Claim key:** `subexponential-rank-one-families-have-zero-restricted-minimax-overhead`
- **Judgment stance:** Supports

## Change: program/finite-rank-one-families/subexponential-zero-overhead

This new node captures the asymptotic theorem derived from the finite-dimensional restricted bound. It is nested beneath that bound because its zero-overhead conclusion depends directly on the bound and the subexponential-cardinality estimates.

## Node: program/finite-rank-one-families/subexponential-witness-limitation

- **Type:** Methodological corollary
- **Title:** Limitation of prescribed subexponential rank-one witness families
- **Status:** Supported with a quantifier restriction
- **Parent:** `program/finite-rank-one-families/subexponential-zero-overhead`

According to the primary judgment, a prescribed sequence of subexponential-size rank-one orientation families cannot by itself witness a positive asymptotic universality price against every codebook.

More precisely, if a lower-bound strategy fixes

\[
\mathcal U_n\subset S^{n-1}
\]

independently of the codebook, with

\[
\ln|\mathcal U_n|=o(n),
\]

and seeks a positive asymptotic lower bound on

\[
\inf_{\substack{C\subset\mathbb R^n\\|C|=M_n}}
\max_{u\in\mathcal U_n}
\left[
r_n-
R_{\mathrm{wf}}
\bigl(nuu^{\mathsf T},D(C,nuu^{\mathsf T})\bigr)
\right],
\]

then the zero restricted-overhead theorem shows that this quantity tends to zero for fixed \(R>0\) and \(M_n=\lceil2^{nR}\rceil\).

Thus fixed finite, polynomial-size, and more generally subexponential-size lists of differently oriented rank-one metrics cannot alone establish a positive asymptotic lower bound against arbitrary codebooks.

The judgment expressly does **not** extend this limitation to:

1. exponentially large rank-one orientation families;
2. a continuum of orientations combined with a uniformity or covering argument;
3. families chosen in a genuinely codebook-dependent way from a larger class;
4. low-rank, higher-rank, or full-rank adversarial metrics; or
5. incompatibility mechanisms not captured by one prescribed subexponential list.

Accordingly, this node rules out only the stated restricted lower-bound mechanism. It does not rule out a positive universality price in the full problem.

### Provenance

- **Primary judgment:** `sha256:240a3302014101ed126cfb505e28cd63f7dda98218281513772886c2d60e1bc5`
- **Subject transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Evidence transaction:** `5e12e53d70d9d24eae78099abae00df3e384d0e3`
- **Claim key:** `subexponential-fixed-rank-one-families-cannot-witness-positive-universality-price`
- **Judgment stance:** Qualifies the corollary by its fixed-family quantifier

## Change: program/finite-rank-one-families/subexponential-witness-limitation

This new node preserves the judgment’s durable methodological consequence while making its quantifier restriction explicit. It is nested under the zero restricted-overhead theorem because that theorem is the sole supplied basis for excluding this particular lower-bound strategy.
