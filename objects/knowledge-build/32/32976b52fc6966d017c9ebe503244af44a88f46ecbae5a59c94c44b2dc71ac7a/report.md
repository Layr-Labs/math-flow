# Knowledge-Formation Report

## Formation basis

This report materializes the conclusions of the following immutable primary judgment without re-evaluating its mathematics:

- **Primary judgment:** `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- **Judged evidence transaction:** `dfc0cc40d41105292a119840dcdbe6f22860cf43`

No conflict records or reconciliation outcomes were supplied. Consequently, there is no conflict requiring an active dispute node. The unresolved exact value of \(D(77)\) is represented as an open mathematical question, not as a dispute between opposed judgments.

The evidence transaction and the judgment itself remain provenance records rather than knowledge nodes.

---

## Node: root

- **Type:** Root research state
- **Status:** Active
- **Parent:** None
- **Primary provenance:** `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

The current judge-established research state for the no-three-in-line problem at grid size \(77\) consists of four durable components:

1. An exact computationally verified existence claim for a 152-point no-three-in-line subset of \(G_{76}\), including a qualification that the associated verifier does not independently check the configuration’s quarter-turn symmetry.
2. A high-confidence certified interval
   \[
   152\le D(77)\le154.
   \]
3. Necessary row and column occupancy constraints for any hypothetical 153- or 154-point no-three-in-line subset of \(G_{77}\).
4. An unresolved exact-value question: the cited judgment does not determine whether \(D(77)\) is \(152\), \(153\), or \(154\), and reports no evidence eliminating or certifying either of the two sizes above the established lower bound.

These components are organized in the following stable nodes:

- `no-three-in-line/g76-152-point-set`
- `no-three-in-line/d77-certified-interval`
- `no-three-in-line/d77-near-capacity-occupancy`
- `no-three-in-line/d77-exact-value`

There are no active adjudicative conflicts in the supplied record.

---

## Node: no-three-in-line/g76-152-point-set

- **Type:** Verified existence claim and certificate scope
- **Status:** Supported
- **Parent:** `root`
- **Primary provenance:** `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- **Evidence transaction:** `dfc0cc40d41105292a119840dcdbe6f22860cf43`

The primary judgment supports, through an exact computational certificate, the existence of a 152-point subset of

\[
G_{76}=\{0,\ldots,75\}^2
\]

containing no three distinct collinear points.

According to the judgment, the supplied payload decodes deterministically into 76 pairs of points, with two points in each row \(y=0,\ldots,75\). The judgment reports that:

- the decoding produces exactly 152 points;
- all decoded coordinates lie in \(\{0,\ldots,75\}^2\);
- the verifier rejects duplicate or out-of-grid points;
- every one of the
  \[
  \binom{152}{3}=573{,}800
  \]
  unordered triples is checked;
- each triple is tested by the integer determinant
  \[
  (x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1);
  \]
- the computation uses exact arbitrary-precision integer arithmetic; and
- no defect is apparent in the encoding or verification logic.

The same judgment therefore characterizes the artifact as a small, self-contained, readily reproducible exact certificate rather than an unsupported search report.

### Scope qualification

The verifier accepts a leading symmetry marker but does not verify quarter-turn symmetry. The judgment states that this omission does not affect certification of the 152-point no-three-in-line property, because that certification uses the explicitly decoded points. Quarter-turn symmetry itself is not independently established by this verifier. This qualification is not a finding that the configuration lacks such symmetry.

### Credit

The judgment carries forward the README’s attribution of the encoded configuration to Achim Flammenkamp’s maintained database. It credits Robert with reproducing the baseline certificate and providing an independent, self-contained verifier, rather than with originating the underlying construction. The finer priority or authorship history of the 152-point construction is not determined by the supplied evidence.

---

## Node: no-three-in-line/d77-certified-interval

- **Type:** Certified bound
- **Status:** Supported with high confidence
- **Parent:** `root`
- **Primary provenance:** `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- **Evidence transaction:** `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- **Related certificate:** `no-three-in-line/g76-152-point-set`

For

\[
G_{77}=\{0,\ldots,76\}^2,
\]

let \(D(77)\) denote the largest size of a subset containing no three distinct collinear points. The primary judgment supports with high confidence the current interval

\[
\boxed{152\le D(77)\le154}.
\]

The judgment attributes the two sides of the interval as follows:

- **Lower bound:** The exact certificate for 152 no-three-in-line points in \(G_{76}\) also supplies 152 such points in \(G_{77}\), because \(G_{76}\subset G_{77}\). Thus the judgment supports
  \[
  D(77)\ge152.
  \]

- **Upper bound:** The judgment accepts the elementary row-capacity argument: each of the 77 horizontal grid lines can contain at most two selected points in a no-three-in-line set. It therefore supports
  \[
  D(77)\le2\cdot77=154.
  \]

The judgment identifies no contradiction between the certificate, verifier, lower-bound implication, and elementary upper bound. It also makes clear that this interval records the established baseline rather than an improvement beyond it.

---

## Node: no-three-in-line/d77-near-capacity-occupancy

- **Type:** Structural necessary conditions
- **Status:** Supported
- **Parent:** `root`
- **Primary provenance:** `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- **Evidence transaction:** `dfc0cc40d41105292a119840dcdbe6f22860cf43`

The primary judgment supports the following necessary occupancy conditions for no-three-in-line subsets of \(G_{77}\) near the upper capacity of 154 points.

### Hypothetical 154-point set

Any valid 154-point subset of \(G_{77}\) must have:

- exactly two selected points in each of the 77 rows; and
- exactly two selected points in each of the 77 columns.

The judgment identifies this as the equality case of the row and column capacity bounds.

### Hypothetical 153-point set

Any valid 153-point subset of \(G_{77}\) must have:

- exactly 76 rows containing two selected points and one row containing one selected point; and
- exactly 76 columns containing two selected points and one column containing one selected point.

The judgment describes this as the precise occupancy pattern associated with a total deficiency of one from the 154-point row and column capacities.

### Scope

These occupancy statements are necessary conditions only. The primary judgment expressly qualifies them as establishing neither existence nor nonexistence of a 153- or 154-point no-three-in-line set. They therefore do not resolve the exact value of \(D(77)\).

---

## Node: no-three-in-line/d77-exact-value

- **Type:** Open mathematical question
- **Status:** Unresolved
- **Parent:** `root`
- **Primary provenance:** `sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`
- **Evidence transaction:** `dfc0cc40d41105292a119840dcdbe6f22860cf43`
- **Related bound:** `no-three-in-line/d77-certified-interval`
- **Related constraints:** `no-three-in-line/d77-near-capacity-occupancy`

The exact value of \(D(77)\) remains unresolved under the supplied primary judgment. The strongest supported conclusion is

\[
152\le D(77)\le154.
\]

The judgment reports that the supplied evidence contains:

- no 153-point certificate;
- no 154-point certificate;
- no global impossibility proof for 153 points;
- no global impossibility proof for 154 points;
- no symmetry-restricted negative result; and
- no reproducible failed search that would provide a narrower, explicitly restricted computational conclusion.

The necessary occupancy conditions for sets of sizes 153 and 154 do not settle their existence or nonexistence.

This unresolved status reflects missing evidence rather than a conflict between opposed judgments. No side of the open question is selected in the current knowledge state.

---

## Change: root

The existing `root` node stated that no judge-authored research programs had been established. It should be revised to provide a holistic index of the durable state now supported by the immutable primary judgment.

The revision replaces the empty-state summary with an organized account of the verified \(G_{76}\) certificate, the \(D(77)\) interval, the near-capacity occupancy constraints, and the unresolved exact value. The evidence transaction is retained as provenance and is not materialized as a research node.

**Justification:** Primary judgment  
`sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

---

## Change: no-three-in-line/g76-152-point-set

This is a proposed new stable node because the existence of a verified 152-point no-three-in-line subset of \(G_{76}\) is a durable mathematical claim independent of transaction names and chronology. It also serves as the certificate foundation for the lower bound at \(n=77\).

The verifier’s quarter-turn-symmetry limitation is incorporated into this node rather than split into a separate node. That limitation qualifies the scope of the same certificate and does not constitute a distinct research program or an opposed mathematical claim.

The credit statement is carried forward exactly at the level supported by the judgment: database attribution for the encoded configuration, verifier and reproducibility credit to Robert, and no determination of finer authorship history.

**Justification:** Primary judgment  
`sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

---

## Change: no-three-in-line/d77-certified-interval

This is a proposed new stable node because the certified interval

\[
152\le D(77)\le154
\]

is the central durable bound for the problem. The lower and upper bounds are kept together because the immutable judgment expressly treats their combination as the strongest supported current conclusion.

The node does not claim an improved bound or exact value. Detailed certificate scope remains in `no-three-in-line/g76-152-point-set`, avoiding duplication while retaining the direct relationship between that certificate and the lower bound.

**Justification:** Primary judgment  
`sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

---

## Change: no-three-in-line/d77-near-capacity-occupancy

This is a proposed new stable node because the occupancy patterns for hypothetical 153- and 154-point sets form a reusable structural constraint distinct from the numerical interval itself.

The two sizes are combined in one node because the judgment presents them as the adjacent capacity and one-deficiency cases of the same row-and-column occupancy principle. The judgment’s qualification that these are necessary but not sufficient conditions is retained as part of the node’s current content.

**Justification:** Primary judgment  
`sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

---

## Change: no-three-in-line/d77-exact-value

This is a proposed new stable node because determining the exact value of \(D(77)\) is a durable open mathematical question distinct from the currently certified interval.

The node records the judgment’s uncertainty and its specific missing-evidence assessment. It is not classified as an active dispute because no opposed primary judgments, conflict records, or unresolved reconciliation outcomes were supplied.

**Justification:** Primary judgment  
`sha256:a470e4a9c0903097d9c860badaa8976cf32ed5336c154f11d8fad980d401f74e`

---

## Conflict and reconciliation audit

- **Conflict records supplied:** None.
- **Conflicts required to remain active:** None.
- **Reconciliation outcomes supplied:** None.
- **Active dispute nodes created:** None.

The unresolved exact value is preserved without choosing among the remaining possibilities, but it is organized as an open question rather than an adjudicative dispute.
