# Two-Term Hierarchical Research Credit Policy

## 1. Purpose

Credit contributions according to the **causal reduction in future research work** that they produce.

At every level of the research hierarchy, the judge estimates only two credit-bearing quantities:

1. **Direct contribution** — expected work avoided on the contribution's own research line.
2. **Obviated work** — expected work avoided on other existing research threads.

The same two quantities are used:

- **ex ante**, by averaging over possible outcomes of the proposed work;
- **ex post**, by evaluating the realized contribution against a matched counterfactual in which the contribution is unavailable.

The central correction is:

> A change in estimated remaining work is not itself credit. It can reflect either causal progress or new information about how difficult the problem really is.

The judge should credit only the **causal work avoided**.

---

## 2. Research Ledger

Each program or subproblem \(v\) maintains a ledger of research threads

\[
\mathcal T_v = \{j_1,\ldots,j_m\}.
\]

A thread may be:

- active;
- queued;
- conditional on another result;
- blocked;
- exploratory;
- a verification or replication effort;
- an unstructured-search bucket;
- completed or retired.

For each thread \(j\), maintain an estimate

\[
b_j(L)
=
\mathbb E[
\text{future work actually spent on }j
\text{ before objective }v\text{ is resolved}
\mid L
].
\]

Here \(L\) is the current ledger state.

This quantity is the thread's **expected exposure**.

It is not the nominal cost of completing the thread if pursued indefinitely. It should already incorporate:

- the probability the thread is actually pursued;
- the probability it is abandoned;
- switching between routes;
- parallel work;
- conditional plans;
- early stopping;
- uncertainty about which route is best.

The ledger's current expected work-to-go estimate is

\[
\widehat W_v(L)
=
\sum_{j\in\mathcal T_v} b_j(L).
\]

Every expected unit of future work should appear in exactly one thread. Maintain a catch-all thread such as **unstructured search and overhead** for future work whose exact form is not yet known.

---

## 3. The Key Counterfactual

For a contribution \(x\), distinguish:

- \(L^{+x}\): the research state when the solver possesses \(x\);
- \(L^{-x}\): a matched counterfactual research state in the **same underlying problem situation**, but where \(x\) and information uniquely inherited from \(x\) are unavailable.

For each affected thread \(j\), define:

\[
b_j^{+x}
=
\text{expected future exposure to thread }j
\text{ with }x,
\]

and

\[
b_j^{-x}
=
\text{expected future exposure to thread }j
\text{ without }x.
\]

Credit is based on

\[
b_j^{-x} - b_j^{+x},
\]

not simply on the difference between the subjective ledger before and after seeing the result.

This prevents useful negative results from being penalized merely because they reveal that the underlying problem is harder than expected.

---

## 4. The Two Credit Terms

Let \(A_x\) denote the direct research line on which contribution \(x\) acts.

### 4.1 Direct contribution

Define

\[
\boxed{
D_x
=
\sum_{j\in A_x}
\left(
b_j^{-x}-b_j^{+x}
\right).
}
\]

This is the expected work causally avoided on the contribution's own line.

It includes value from:

- calculations completed;
- experiments completed;
- lemmas proved;
- uncertainty resolved;
- tools constructed;
- intermediate states produced.

It must be **net of follow-up work** created by the contribution.

For example, a result that removes 50 hours of derivation but creates 20 hours of necessary implementation work has direct value 30 hours, not 50.

### 4.2 Obviated work

Define

\[
\boxed{
O_x
=
\sum_{j\notin A_x}
\left(
b_j^{-x}-b_j^{+x}
\right).
}
\]

This is the expected work causally avoided on other existing ledgered threads.

It may include reductions in:

- competing solution routes;
- redundant implementations;
- hypotheses that no longer need testing;
- verification paths made unnecessary;
- duplicate work by other teams;
- debugging or repair work avoided;
- unstructured search.

"Obviated" should be interpreted as **reduced expected future exposure**, not only complete cancellation.

A contribution that reduces a thread's expected exposure from 40 hours to 10 hours receives 30 hours of obviation value from that thread.

### 4.3 Total local score

The local causal work-value score is

\[
\boxed{
S_x = D_x + O_x.
}
\]

Equivalently,

\[
S_x
=
W^{-x}-W^{+x},
\]

where

\[
W^{-x}
=
\sum_j b_j^{-x},
\qquad
W^{+x}
=
\sum_j b_j^{+x}.
\]

The two terms are therefore not independent bonuses. They partition one underlying quantity:

> **How much more work would a competent solver expect to perform if this contribution were unavailable?**

---

## 5. News About Difficulty

Let

\[
W_{\text{before}}
\]

be the subjective expected remaining work before observing the contribution, and let

\[
W_{\text{after}}
=
W^{+x}
\]

be the subjective expected remaining work after incorporating it.

The observed change

\[
W_{\text{before}} - W_{\text{after}}
\]

contains two conceptually different pieces:

\[
\boxed{
W_{\text{before}} - W_{\text{after}}
=
S_x + N_x,
}
\]

where

\[
S_x
=
W^{-x}-W^{+x}
\]

is causal work saved, and

\[
N_x
=
W_{\text{before}}-W^{-x}
\]

is **news about latent difficulty**.

### Example: useful bad news

Suppose:

\[
W_{\text{before}}=100.
\]

A contribution proves that the currently favored route is impossible. After learning this,

\[
W^{+x}=150.
\]

But without possessing the proof, a competent solver in the same realized problem would have wasted another 30 hours pursuing the dead route:

\[
W^{-x}=180.
\]

Then:

\[
S_x = 180-150=30,
\]

while

\[
N_x = 100-180=-80.
\]

Thus:

\[
-50 = 30 + (-80).
\]

The contribution **saved 30 hours**, while revealing that the underlying problem was 80 hours harder than previously believed.

The judge should credit the 30 hours and treat the \(-80\) hours as news, not as negative contribution.

---

## 6. Ex-Ante Judging

The ex-ante judge sees:

- the complete current ledger;
- the proposed work;
- its target thread or program;
- its expected cost;
- current dependencies;
- current alternative routes.

The judge considers the possible outcomes \(o\) of performing the work and estimates, for each outcome, the matched counterfactual:

\[
D_x(o), \qquad O_x(o).
\]

The reported ex-ante values are:

\[
\boxed{
D_x^{\mathrm{ante}}
=
\mathbb E_o[D_x(o)]
}
\]

and

\[
\boxed{
O_x^{\mathrm{ante}}
=
\mathbb E_o[O_x(o)].
}
\]

The total is

\[
\boxed{
S_x^{\mathrm{ante}}
=
D_x^{\mathrm{ante}}
+
O_x^{\mathrm{ante}}.
}
\]

The judge may internally consider outcomes such as:

- intended success;
- partial reusable progress;
- informative negative result;
- uninformative failure;
- misleading result.

It does not need to output a separate score for each outcome.

### Ex-ante judging question

> If this work is performed, how much future work do we expect its possible results to causally eliminate on its direct research line, and how much future work do we expect them to eliminate on other existing ledgered threads?

This formulation automatically incorporates:

- probability of success;
- probability the result will ultimately matter;
- replacement difficulty;
- uncertainty over alternative routes;
- pruning value;
- useful negative results.

These do not need separate reward terms.

---

## 7. Ex-Post Judging

The ex-post judge receives:

- the pre-contribution ledger snapshot;
- the contribution;
- subsequent ledger history;
- the full research trace;
- the final solution or final state;
- the dependency and provenance graph.

The full trace is used to determine:

- what the contribution actually produced;
- which later work descended from it;
- which threads it genuinely made unnecessary;
- whether apparent obviation was temporary or mistaken;
- whether it played an indirect causal role.

The judge then constructs the matched counterfactual:

> Hold fixed the realized underlying problem. Remove the contribution and information uniquely inherited from it. Let a competent solver adapt optimally from that state. How much additional future work would be required?

The ex-post judge reports:

\[
\boxed{
D_x^{\mathrm{post}}
}
\]

and

\[
\boxed{
O_x^{\mathrm{post}}.
}
\]

with

\[
\boxed{
S_x^{\mathrm{post}}
=
D_x^{\mathrm{post}}
+
O_x^{\mathrm{post}}.
}
\]

### Ex-post judging question

> Given what actually happened, how much additional work would a competent solver have needed on this contribution's direct line, and on other ledgered lines, if this contribution had not been available?

### Treatment of unsuccessful work

Unsuccessful work can receive positive ex-post achievement credit when it:

- produces a useful negative result;
- rules out a route;
- prevents repetition of a failed approach;
- retires an existing thread;
- supplies a reusable intermediate result;
- changes the search policy in a way that saves later work.

Work that was sensible ex ante but produced no usable state change and obviated no future work receives approximately zero ex-post achievement credit.

Its quality as a research decision may be recorded separately, but no additional achievement-credit term is required.

---

## 8. Ex-Ante / Ex-Post Calibration

The ex-ante judge should estimate the expectation of the same causal quantity later measured ex post.

Ideally:

\[
\boxed{
\mathbb E[
D_x^{\mathrm{post}}
\mid \text{pre-state},x
]
=
D_x^{\mathrm{ante}}
}
\]

and

\[
\boxed{
\mathbb E[
O_x^{\mathrm{post}}
\mid \text{pre-state},x
]
=
O_x^{\mathrm{ante}}.
}
\]

Therefore:

\[
\boxed{
\mathbb E[
S_x^{\mathrm{post}}
\mid \text{pre-state},x
]
=
S_x^{\mathrm{ante}}.
}
\]

The difference

\[
S_x^{\mathrm{post}} - S_x^{\mathrm{ante}}
\]

is realized upside, downside, or luck.

Across similarly judged contributions, this residual should average to approximately zero if the ex-ante judge is calibrated.

Ex-ante and ex-post credit should **not be added together**. Ex-ante credit is a forecast of ex-post credit, not a second source of value.

---

## 9. Hierarchical Allocation

Every program node \(v\) receives a parent-level credit pot \(C_v\).

Its internal contributions or child programs receive local scores:

\[
S_{u\mid v}
=
D_{u\mid v}
+
O_{u\mid v}.
\]

These scores determine each child's share of the parent pot.

For positive achievement allocation, define:

\[
\alpha_{u\mid v}
=
\frac{S_{u\mid v}^{+}}
{
\sum_{w\in \operatorname{children}(v)}
S_{w\mid v}^{+}
+
S_{\mathrm{unattributed},v}
},
\]

where

\[
S^+ = \max(S,0).
\]

Then:

\[
\boxed{
C_u
=
\alpha_{u\mid v} C_v.
}
\]

The unattributed term is a virtual child representing value that cannot yet be assigned confidently.

Negative scores should be retained in a separate harm or error ledger rather than silently redistributed.

The procedure recurses down the hierarchy.

For a leaf contribution \(x\):

\[
C_x
=
C_{\mathrm{root}}
\prod_{(v\rightarrow u)\in \mathrm{path}(x)}
\alpha_{u\mid v}.
\]

This gives exact hierarchical budget balance.

---

## 10. Speculative Programs

Suppose a speculative program \(A\) initially looks unlikely to succeed.

At the parent level, its ex-ante expected credit may be small because its expected effect on the parent research state is small.

Inside \(A\), however, contributions can make substantial local progress.

Let their local scores be:

\[
S_1^A,\ldots,S_k^A.
\]

These determine conditional internal shares:

\[
\alpha_i^A
=
\frac{(S_i^A)^+}
{\sum_j (S_j^A)^+}.
\]

If \(A\) fails, its parent credit pot may remain small or zero.

If \(A\) succeeds and thereby obviates a large amount of parent-level work, it receives a large realized credit pot \(C_A\), which is then distributed according to the internal shares:

\[
C_i
=
\alpha_i^A C_A.
\]

This separates:

1. **progress toward completing the speculative program**, from
2. **the program's eventual importance to the larger solution**.

The final completion step therefore does not automatically capture all of the program's realized value.

---

## 11. Conservation Principles

### 11.1 Counterfactual work conservation

At a given node, the fundamental causal quantity is:

\[
\boxed{
S_x
=
D_x+O_x
=
W^{-x}-W^{+x}.
}
\]

The direct and obviated terms must sum to the total matched-counterfactual work difference.

If they do not, the discrepancy should be retained as a residual rather than forced into one category.

### 11.2 Observed-\(W\) decomposition

Changes in the subjective estimate of remaining work satisfy:

\[
\boxed{
W_{\text{before}}-W_{\text{after}}
=
S_x+N_x,
}
\]

where \(N_x\) is news about latent difficulty.

This is the correct replacement for the naive rule:

\[
S_x
\stackrel{\text{wrong}}{=}
W_{\text{before}}-W_{\text{after}}.
\]

For pure information revelation, a calibrated judge should have:

\[
\mathbb E[N_x\mid \text{pre-state}] = 0.
\]

Thus news can be strongly positive or negative on a realized trajectory while averaging to zero over calibrated cases.

### 11.3 Research-process conservation

If \(W_t\) is correctly defined as conditional expected remaining work under a fixed reference policy, and \(C_t\) is cumulative work already spent, then:

\[
C_t + W_t
=
\mathbb E[C_\tau\mid \mathcal F_t]
\]

is a martingale.

Therefore:

\[
\mathbb E[
W_t-W_{t+1}
\mid \mathcal F_t
]
=
\mathbb E[
C_{t+1}-C_t
\mid \mathcal F_t
].
\]

In words:

> One unit of work performed reduces expected remaining work by one unit in expectation.

This is a calibration principle for the overall work model, not a rule that every realized contribution must have credit equal to its cost.

### 11.4 Hierarchical conservation

At every node:

\[
\boxed{
\sum_{u\in\operatorname{children}(v)}
C_u
+
C_{\mathrm{unattributed},v}
=
C_v.
}
\]

Consequently, leaf credits plus retained residuals sum exactly to the root credit pot.

This is the primary accounting constraint that prevents double counting across levels.

---

## 12. Scoping Rules

### Use expected exposure, not nominal thread size

If a thread would require 1,000 hours if fully pursued but has only a 10% chance of being pursued, its expected exposure may be approximately 100 hours, not 1,000.

### Count only future work

Work already completed is sunk. A contribution can only save work that would otherwise occur after the relevant reference state.

### Anchor alternatives to the ledger

The judge should not invent arbitrary counterfactual research programs after seeing the result.

Potential future work should already appear as:

- a named thread;
- a queued conditional thread;
- an exploration budget;
- an unstructured-search exposure.

### Allow optimal adaptation

"Without \(x\)" does not mean "continue the historical plan blindly."

The counterfactual solver may switch routes, abandon work, substitute another method, or recover an equivalent result by another route.

Credit is the **minimum expected additional work caused by withholding \(x\)** under competent adaptive continuation.

### Subtract follow-up work

A contribution that opens a shortcut but creates substantial implementation, verification, or integration work receives credit only for the net reduction.

### Treat partial displacement as obviation

A thread need not disappear completely. Any reduction in expected future exposure counts.

### Count each causal reduction once

The same unit of future work must not be claimed both as direct progress and as obviated work.

### Score only immediate-parent effects

A contribution should not separately claim:

- its effect on its local program;
- the program's effect on a subproblem;
- the subproblem's effect on the final solution.

Only the immediate hierarchical edge is scored. Downstream value propagates through the hierarchy.

### Do not reward pure news as causal progress

A contribution does not deserve credit merely because it reveals that the problem was easier than expected.

Likewise, it should not be penalized merely because it reveals that the problem was harder than expected.

Only the difference between **with-contribution** and **without-contribution** work in the matched problem state counts as achievement credit.

---

## 13. Minimal Judge Output

### Ex-Ante

```text
Contribution:
Parent objective:
Direct thread/program:
Ledger snapshot:

Expected direct work avoided:
D_ante =

Other ledgered work expected to be obviated:
- Thread ID:
  Expected exposure without contribution:
  Expected exposure with contribution:
  Reason:

Expected obviated work:
O_ante =

Total expected local score:
S_ante = D_ante + O_ante

Estimated cost of performing contribution:
Confidence:
Ledger evidence:
```

### Ex-Post

```text
Contribution:
Parent objective:
Direct thread/program:
Pre-contribution ledger snapshot:

Matched counterfactual:
What information is removed?
What independent information is retained?
How may the solver adapt?

Realized direct work avoided:
D_post =

Other ledgered work causally obviated:
- Thread ID:
  Expected exposure without contribution:
  Expected exposure with contribution:
  Causal explanation:

Realized obviated work:
O_post =

Total realized local score:
S_post = D_post + O_post

Observed change in subjective remaining work:
Delta_W_observed =

Implied news about difficulty:
N = Delta_W_observed - S_post

Difference from ex-ante forecast:
S_post - S_ante =

Confidence:
Ledger/provenance evidence:
```

---

## 14. Recommended Default Interpretation

The judge should think in terms of only two reward-bearing questions:

\[
\boxed{
\textbf{Direct contribution}
=
\text{How much future work on this research line exists without this contribution but not with it?}
}
\]

and

\[
\boxed{
\textbf{Obviated work}
=
\text{How much future work on other existing research lines exists without this contribution but not with it?}
}
\]

Everything else should be treated as either:

- evidence used to answer these questions;
- news about latent difficulty;
- a hierarchical propagation effect;
- or an explicit residual.

This keeps the judge's task simple while preserving the expected-work interpretation, useful negative results, speculative-program credit, and hierarchical conservation.
