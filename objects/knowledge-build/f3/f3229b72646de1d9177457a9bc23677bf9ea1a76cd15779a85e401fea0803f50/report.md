# Knowledge-Formation Report: The Sixth Schur Number

## Node: root

**Title:** Research state for the sixth Schur number  
**Type:** Root  
**Status:** Active

### Current knowledge

The central unresolved question is the exact value of the sixth Schur number \(S(6)\), the largest \(N\) for which \(\{1,\ldots,N\}\) admits a six-coloring with no monochromatic solution of

\[
x+y=z,
\]

including solutions with \(x=y\).

The immutable primary judgments currently support the interval

\[
536\le S(6)\le1836.
\]

Primary judgment `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4` supports the lower endpoint with high confidence through a complete explicit six-coloring of \(\{1,\ldots,536\}\) and exact exhaustive verification. Primary judgments `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b` and `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1` provide further corroboration of the same fixed Fredricksen–Sweet coloring and its baseline verification.

The latest judgment expressly finds that the radius-\(60\) work is local to a neighborhood of that fixed labeled coloring. Even if its proposed local exclusion were fully certified, it would leave open colorings through \(537\) at Hamming distance at least \(61\) from the baseline. Consequently, the supplied judgments support none of the following:

- a coloring of \(\{1,\ldots,537\}\);
- a lower bound \(S(6)\ge537\);
- a global impossibility proof at \(537\) or any other improved threshold;
- a reduction of the upper endpoint \(1836\); or
- an exact determination of \(S(6)\).

The current global account therefore remains

\[
536\le S(6)\le1836,
\]

with both the exact-value question and the gap between the endpoints unresolved.

### Program organization

One durable research program remains established directly under the root:

- `programs/explicit-coloring-certificates` — explicit finite coloring witnesses, exact deterministic verification, and certificate-relative local-extension analysis.

The radius-\(43\) and radius-\(60\) investigations remain within that program because both are defined relative to the same fixed Fredricksen–Sweet coloring through \(536\). They do not constitute independent global upper-bound programs.

The exact-value question and current global bounds remain at root because they span all possible approaches to \(S(6)\).

### Conflict and uncertainty state

No conflict or reconciliation records were supplied. There is therefore no active dispute node.

The missing LRAT payloads for the radius-\(43\) and radius-\(60\) exclusion claims create evidentiary uncertainty, not a conflict between opposed judgments. Those claims remain qualified within their respective stable nodes.

### Provenance

- **Primary judgment supporting the baseline and original global account:** `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4`
- **Primary judgment supporting the radius-\(43\) reduction and unchanged bounds:** `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`
- **Primary judgment supporting the radius-\(60\) reduction and unchanged bounds:** `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`
- **Transactions:**
  - `b28dd977ae39eb77989de8e60b63f7eacd8982d2`, ledger position 1
  - `26a77f38a16f35641a8d8f0efe72132953af5d2e`, ledger position 2
  - `6a72758caaeb34a56d8d55653c8a3184ffbbe65e`, ledger position 3
- **Relevant latest claim key:** `schur-number-6/bounds-unchanged`

## Change: root

The root is updated to incorporate the latest judgment’s explicit conclusion that the radius-\(60\) investigation is non-global and warrants no change to \(536\le S(6)\le1836\). The local result and its missing certificates are organized under the existing explicit-coloring program rather than promoted to a new root-level agenda.

## Node: programs/explicit-coloring-certificates

**Title:** Explicit coloring certificates, exact verification, and certificate-relative extension analysis  
**Type:** Program  
**Parent:** `root`  
**Status:** Active

### Program scope

This program organizes durable work based on explicit finite Schur colorings and exact machinery for checking or analyzing them. Its current scope includes:

- complete finite coloring witnesses;
- compact and expanded witness encodings;
- exact checks of syntax, coverage, color ranges, and representation agreement;
- exhaustive verification of the Schur condition;
- combinatorial analysis of attempts to extend a fixed certified coloring;
- Hamming-distance decompositions relative to a fixed baseline;
- exact SAT encodings of bounded local-extension questions;
- replayable RUP/LRAT proof-checking architectures; and
- qualification of local exclusion claims whose decisive proof payloads are unavailable.

The local-extension work remains in this program because the questions are explicitly measured from the fixed Fredricksen–Sweet coloring

\[
B:\{1,\ldots,536\}\to\{1,\ldots,6\}.
\]

Neither the radius-\(43\) nor radius-\(60\) investigation is a general impossibility argument for all colorings through \(537\).

### Current program knowledge

The program contains the following durable concepts:

1. `programs/explicit-coloring-certificates/coloring-1-536` records the strongly supported Fredricksen–Sweet six-coloring of \(\{1,\ldots,536\}\), its agreeing representations, and its certification of \(S(6)\ge536\).

2. `programs/explicit-coloring-certificates/exact-checker-536` records exact deterministic verification of that fixed certificate, including exhaustive checking of all \(71{,}824\) relevant Schur triples through \(536\).

3. `programs/explicit-coloring-certificates/blocker-pairs-at-537` records the blocker-pair counts

   \[
   (64,43,55,38,32,35)
   \]

   for assigning each possible color to \(537\), together with the direct exclusions those counts provide at specified Hamming radii.

4. `programs/explicit-coloring-certificates/hamming-distance-decomposition-at-537` records the exact decomposition of distance from the baseline into mandatory blocker changes and extra changes. It now organizes both the radius-\(43\) and radius-\(60\) case splits.

5. `programs/explicit-coloring-certificates/sat-lrat-radius-43-method` records the previously supported SAT encoding and RUP-only LRAT checking architecture for the conditioned radius-\(43\) cases.

6. `programs/explicit-coloring-certificates/radius-43-exclusion-at-537` records the proposed universal radius-\(43\) local exclusion. The supplied judgments do not establish that theorem because four referenced LRAT proof payloads are absent.

7. `programs/explicit-coloring-certificates/sat-lrat-radius-60-method` records the supported reduction of the radius-\(60\) question to five faithful conditioned CNFs, along with the proposed strict ordered-RUP replay architecture.

8. `programs/explicit-coloring-certificates/radius-60-exclusion-at-537` records the claim that every valid labeled coloring through \(537\) differs from the baseline in at least \(61\) old coordinates. The claim is not established by the supplied artifacts because all five decisive LRAT payloads are absent.

The judgments support the baseline certificate, blocker analysis, exact distance accounting, and the faithfulness of the radius-\(43\) and radius-\(60\) finite reductions. They do not support the asserted unsatisfiability of the conditioned formulas without the referenced proof files.

### Frontier limitations

The program currently contains:

- no certified coloring of \(\{1,\ldots,537\}\) or a larger interval;
- no proof excluding every six-coloring of \(\{1,\ldots,537\}\);
- no improvement to the lower endpoint \(536\);
- no improvement to the upper endpoint \(1836\); and
- no determination of \(S(6)\).

Even a completed radius-\(60\) exclusion would only exclude the closed Hamming ball of radius \(60\) around one fixed labeled baseline on the first \(536\) coordinates.

### Attribution

The judgments carry forward attribution of the underlying \(536\)-coloring and published lower bound to Harold Fredricksen and Melvin M. Sweet. None of the assessed transactions claims originality for that coloring or for \(S(6)\ge536\).

The radius-\(43\) judgment attributes the local decomposition, exact CNF construction, independent RUP/LRAT checker, and reproduction design to the work assessed there. Its metadata attributes intended proof generation to CaDiCaL and workflow implementation to an OpenAI Codex research agent acting at Robert Raynor’s request. That judgment makes no priority determination for the uncertified local theorem.

The radius-\(60\) judgment identifies the distinct work of its subject as the stronger local-neighborhood formulation, blocker-based distance encoding, five conditioned SAT instances, claimed production and trimming of RUP-only LRAT proofs, and replay tooling. Because the decisive proof files are absent, the judgment recognizes a convincing exact reduction and certificate framework, not an independently verified radius-\(60\) theorem.

### Provenance

- **Primary judgments:**
  - `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4`
  - `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`
  - `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`
- **Transactions:**
  - `b28dd977ae39eb77989de8e60b63f7eacd8982d2`, ledger position 1
  - `26a77f38a16f35641a8d8f0efe72132953af5d2e`, ledger position 2
  - `6a72758caaeb34a56d8d55653c8a3184ffbbe65e`, ledger position 3
- **Conflict records:** none supplied

## Change: programs/explicit-coloring-certificates

The program is expanded, without changing its established boundary, to organize the distinct radius-\(60\) conditioned SAT/LRAT method and exclusion claim. No new root-level program is created because the new work remains dependent on the fixed Fredricksen–Sweet baseline and has only local, certificate-relative scope.

## Node: programs/explicit-coloring-certificates/coloring-1-536

**Title:** Certified six-coloring of \(\{1,\ldots,536\}\)  
**Type:** Result  
**Parent:** `programs/explicit-coloring-certificates`  
**Status:** Supported with high confidence

### Current knowledge

Primary judgments

- `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4`,
- `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`, and
- `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`

support the proposition

\[
\{1,\ldots,536\}\text{ admits a six-coloring with no monochromatic }x+y=z.
\]

They accordingly support

\[
S(6)\ge536.
\]

This certifies the published lower endpoint but does not improve it.

### Witness and representations

The fixed Fredricksen–Sweet certificate assigns exactly one color in \(\{1,\ldots,6\}\) to every integer from \(1\) through \(536\).

The earlier judgment reports two agreeing representations:

- a compact representation based on the involution
  \[
  r\longmapsto537-r;
  \]
- a canonical expanded CSV containing one row for each integer \(1,\ldots,536\).

The ordinary compact representatives are the smaller elements of complementary pairs, with both endpoints assigned the same color. The pair

\[
\{179,358\}
\]

is exceptional, with assignments

\[
179\mapsto4,\qquad358\mapsto1.
\]

The reported class sizes are

\[
129,\ 86,\ 110,\ 77,\ 64,\ 70,
\]

which sum to \(536\) and agree with the compact paired representation and exceptional assignments.

The symmetry is a representation device, not a substitute for checking all Schur triples. None of the judgments identifies the asymmetric exceptional pair as a mathematical defect.

### Exact certification and corroboration

The original checker exhaustively tests every pair satisfying

\[
1\le x\le y,\qquad x+y\le536,
\]

including \(x=y\). The number of tested triples is

\[
71{,}824.
\]

The radius-\(43\) judgment reports that its transaction duplicates the baseline data entry-for-entry and independently repeats the exact baseline check.

The radius-\(60\) judgment reports that its subject supplies the complete expanded `baseline-536.csv`, identifies it with the same canonical Fredricksen–Sweet witness, and fixes its SHA-256 digest as

```text
5e2cd4854c20e8441ff52e09e02472657309d35eb4b35c6957a1be37f6a8cbc9
```

That judgment also accepts the included exact baseline checker as covering all \(71{,}824\) unordered Schur triples, including \(x=y\). It finds that all witness bytes needed for independent replay are present.

These later checks corroborate the same fixed coloring. They do not provide distinct colorings or stronger lower bounds.

### Structural role at \(537\)

The complementary-pair structure of this certificate supports:

- the blocker counts recorded in `programs/explicit-coloring-certificates/blocker-pairs-at-537`;
- the exact distance identity recorded in `programs/explicit-coloring-certificates/hamming-distance-decomposition-at-537`; and
- the radius-\(43\) and radius-\(60\) conditioned SAT reductions.

Those conclusions concern proximity to this fixed labeled baseline. They do not imply that a more distant coloring through \(537\) cannot exist.

### Evidentiary qualifications

The complete witness and checker sources needed for independent baseline replay are supplied. The judgments nevertheless record no execution transcript, hosted acceptance artifact, signed attestation, or other independent observation of an execution on the exact submitted bytes.

The absence of LRAT payloads for the radius-\(43\) and radius-\(60\) local theorems does not undermine the baseline coloring certificate. Those missing files concern later unsatisfiability claims, not the explicit coloring through \(536\).

No construction history is required for the finite lower-bound proof. None of the judgments supports a coloring through \(537\) or a larger interval.

### Attribution and provenance

The documentation assessed by all three judgments attributes the underlying coloring to Harold Fredricksen and Melvin M. Sweet. The transactions claim no originality for the coloring or lower bound. Their assessed contributions concern transcription, packaging, verification, and certificate-relative use of the fixed witness.

- **Primary judgments:**
  - `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4`
  - `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`
  - `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`
- **Transactions:**
  - `b28dd977ae39eb77989de8e60b63f7eacd8982d2`
  - `26a77f38a16f35641a8d8f0efe72132953af5d2e`
  - `6a72758caaeb34a56d8d55653c8a3184ffbbe65e`
- **Relevant latest claim key:** `fredricksen-sweet-536/sum-free-six-coloring`

## Change: programs/explicit-coloring-certificates/coloring-1-536

The node gains the latest judgment’s additional support: a complete expanded copy of the same baseline, its recorded digest, and another exact checker with all witness bytes available for replay. This is corroboration of the existing stable result, not a new coloring or bound.

## Node: programs/explicit-coloring-certificates/exact-checker-536

**Title:** Exact exhaustive verification of the fixed \(536\)-integer coloring certificate  
**Type:** Method  
**Parent:** `programs/explicit-coloring-certificates`  
**Status:** Supported for the fixed certificate format

### Current knowledge

Primary judgment `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4` finds the original deterministic Python checker logically correct for the supplied six-coloring of \(\{1,\ldots,536\}\).

Primary judgment `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b` reports that a later verifier independently repeats the baseline check and uses baseline data agreeing entry-for-entry with the original certificate.

Primary judgment `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1` reports a further complete expanded baseline and exact checker. It finds the checker logic straightforward, deterministic, and independently replayable from the supplied witness bytes.

### Original fixed-format validation

The original checker uses exact Python integer arithmetic and no floating-point calculations, randomness, heuristic solver behavior, timeout dependence, or external package dependency.

For the compact representation, it:

- requires the expected JSON fields;
- rejects booleans and other non-integer values where integers are required;
- fixes \(n=536\), six colors, and symmetry modulus \(537\);
- requires six paired-class lists;
- checks
  \[
  1\le r<537-r\le536
  \]
  for every ordinary representative;
- rejects overlapping or repeated assignments;
- range-checks exceptional assignments and colors; and
- verifies exact coverage of \(\{1,\ldots,536\}\).

For the expanded CSV, it:

- requires the exact header `integer,color`;
- requires exactly \(536\) data rows;
- requires row \(i\) to encode integer \(i\);
- restricts colors to \(\{1,\ldots,6\}\); and
- enforces ASCII and canonical decimal syntax.

The original checker requires exact agreement between the expanded compact witness and the CSV assignment.

### Additional expanded-witness validation

The latest judgment reports that the radius-\(60\) verifier checks:

1. exact CSV syntax and canonical row order;
2. one color in \(\{1,\ldots,6\}\) for every integer \(1,\ldots,536\);
3. use of all six colors; and
4. every triple satisfying
   \[
   1\le x\le y,\qquad x+y\le536.
   \]

Its baseline file is recorded with SHA-256 digest

```text
5e2cd4854c20e8441ff52e09e02472657309d35eb4b35c6957a1be37f6a8cbc9
```

and identified with the same canonical Fredricksen–Sweet coloring.

### Exhaustive Schur verification

The checkers enumerate every pair satisfying

\[
1\le x\le y,\qquad x+y\le536
\]

and test whether \(x\), \(y\), and \(x+y\) all have the same color. This includes \(x=y\) and covers every relevant Schur triple once up to interchange of the summands.

The judgments accept the exact count

\[
\sum_{x=1}^{268}(537-2x)=268^2=71{,}824.
\]

No search failure, heuristic inference, or probabilistic computation is used in this baseline verification.

### Scope

The original dual-representation method is specialized to:

- \(n=536\);
- six colors; and
- symmetry modulus \(537\).

It is an exact checker for the fixed certificate format, not a general verifier for arbitrary Schur-number instances.

The expanded CSV is canonical for a labeled coloring only. It fixes row order and syntax but does not identify colorings that differ by a permutation of color labels.

The later baseline routines provide additional exact checks of the same mathematical witness. Their SAT and LRAT functionality belongs to the separate radius-specific method nodes.

### Replay status

The original source and expected successful output are available, but the earlier judgment records no separate execution transcript, hosted attestation, or signed acceptance for the exact submitted bytes.

The later transactions provide additional verifier source and complete baseline data. The latest judgment finds that all witness bytes needed for independent replay are present, while also noting that no execution attestation was supplied and that the large finite enumeration was not itself observed in that judgment.

Missing LRAT payloads prevent replay of the separate local exclusion claims. They do not affect the logic or artifact completeness of the baseline coloring check.

### Provenance

- **Primary judgments:**
  - `sha256:8ec8f005952dfe36611e70f5c11fc631845f5275a391ec498f1f65448c3918f4`
  - `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`
  - `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`
- **Transactions:**
  - `b28dd977ae39eb77989de8e60b63f7eacd8982d2`
  - `26a77f38a16f35641a8d8f0efe72132953af5d2e`
  - `6a72758caaeb34a56d8d55653c8a3184ffbbe65e`
- **Relevant latest claim key:** `fredricksen-sweet-536/sum-free-six-coloring`

## Change: programs/explicit-coloring-certificates/exact-checker-536

The node is updated with the third judgment’s corroborating expanded-witness checker, recorded baseline digest, and replay assessment. The update does not broaden the method into a general Schur verifier and does not merge the separate SAT/LRAT certification machinery into this baseline-checker node.

## Node: programs/explicit-coloring-certificates/blocker-pairs-at-537

**Title:** Blocker pairs for assigning a color to \(537\) relative to the fixed baseline  
**Type:** Lemma  
**Parent:** `programs/explicit-coloring-certificates`  
**Status:** Supported

### Current knowledge

Primary judgments

- `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`, and
- `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`

support the blocker-pair analysis relative to the fixed Fredricksen–Sweet coloring

\[
B:\{1,\ldots,536\}\to\{1,\ldots,6\}.
\]

For a prospective extension \(C\) and a fixed color \(c=C(537)\), consider

\[
\{x,537-x\},\qquad1\le x\le268.
\]

Because \(537\) is odd, these \(268\) pairs are pairwise disjoint and partition the first \(536\) coordinates.

A pair is a color-\(c\) blocker when both endpoints have baseline color \(c\). If both baseline assignments were retained while \(C(537)=c\), the pair and \(537\) would form the monochromatic equation

\[
x+(537-x)=537.
\]

Every color-\(c\) blocker therefore forces at least one old coordinate to change.

### Supported blocker counts

The judgments support

\[
(b_1,b_2,b_3,b_4,b_5,b_6)
=
(64,43,55,38,32,35).
\]

Their sum is

\[
64+43+55+38+32+35=267.
\]

This agrees with the \(267\) ordinary same-color complementary pairs in the compact baseline representation. The remaining pair,

\[
\{179,358\},
\]

has different baseline colors \(4\) and \(1\), so it is not a blocker for any single color.

The counts also agree with the baseline class sizes

\[
129,\ 86,\ 110,\ 77,\ 64,\ 70:
\]

- color \(1\) has \(64\) ordinary pairs and exceptional point \(358\);
- color \(4\) has \(38\) ordinary pairs and exceptional point \(179\);
- each other class consists of twice its blocker count.

### Mandatory-change consequences

If \(C(537)=c\), at least \(b_c\) positions among \(1,\ldots,536\) must differ from the baseline. In particular:

| \(C(537)\) | Mandatory old-coordinate changes |
|---:|---:|
| \(1\) | \(64\) |
| \(2\) | \(43\) |
| \(3\) | \(55\) |
| \(4\) | \(38\) |
| \(5\) | \(32\) |
| \(6\) | \(35\) |

Consequently:

- within Hamming radius \(43\), colors \(1\) and \(3\) for \(537\) are directly excluded;
- within Hamming radius \(60\), color \(1\) for \(537\) is directly excluded.

The second conclusion does not require SAT solving or an LRAT certificate. The other five colors are not excluded at radius \(60\) by blocker counts alone.

### Scope

This lemma establishes mandatory changes relative to one fixed labeled baseline. It does not exclude all six-colorings through \(537\), does not exclude colorings beyond the stated radii, and does not change either endpoint of the current interval for \(S(6)\).

### Provenance

- **Primary judgments:**
  - `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`
  - `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`
- **Transactions:**
  - baseline: `b28dd977ae39eb77989de8e60b63f7eacd8982d2`
  - radius-\(43\) analysis: `26a77f38a16f35641a8d8f0efe72132953af5d2e`
  - radius-\(60\) analysis: `6a72758caaeb34a56d8d55653c8a3184ffbbe65e`
- **Relevant claim keys:**
  - `fs536-blocker-pair-counts-at-537`
  - `radius-60/blocker-distance-decomposition`

## Change: programs/explicit-coloring-certificates/blocker-pairs-at-537

The node is generalized to record the latest judgment’s radius-\(60\) use of the already supported blocker counts. The mathematical blocker lemma is unchanged; its complete current consequences now include the direct exclusion of \(C(537)=1\) from the closed radius-\(60\) ball.

## Node: programs/explicit-coloring-certificates/hamming-distance-decomposition-at-537

**Title:** Hamming-distance decomposition for extensions through \(537\)  
**Type:** Lemma  
**Parent:** `programs/explicit-coloring-certificates`  
**Status:** Supported

### Current knowledge

Primary judgments

- `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`, and
- `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`

support an exact decomposition of Hamming distance from the fixed baseline \(B\).

Fix \(c=C(537)\), and let \(b_c\) be the number of baseline color-\(c\) blocker pairs. Every blocker pair contributes at least one mandatory changed endpoint. Because the pairs are disjoint, every change beyond those \(b_c\) mandatory changes is exactly one of:

1. a second changed endpoint in a blocker pair; or
2. a changed integer outside all color-\(c\) blocker pairs.

Thus the judgments support

\[
d_H\!\left(C|_{\{1,\ldots,536\}},B\right)
=
b_c+\#\{\text{extra changes}\}.
\]

This is exact accounting, not merely a lower-bound heuristic.

### Auxiliary-variable form

For a blocker pair \(\{x,y\}\), the radius-\(60\) verifier uses an auxiliary variable \(e_{x,y}\) indicating that both endpoints change. The relevant clauses are reported as

\[
\neg e_{x,y}\lor\neg X(x,B(x)),
\]

\[
\neg e_{x,y}\lor\neg X(y,B(y)),
\]

and

\[
X(x,B(x))\lor X(y,B(y))\lor e_{x,y}.
\]

Under the exactly-one-color constraints, the latest judgment finds that these clauses make \(e_{x,y}\) true exactly when both endpoints differ from their baseline colors. The counted literals consisting of these auxiliaries and the changes outside blocker pairs therefore represent exactly the extra-change term.

### Radius-\(43\) decomposition

Colors \(1\) and \(3\) are directly excluded at radius \(43\) because their blocker counts exceed \(43\). The remaining cases are:

| \(C(537)\) | \(b_c\) | Maximum extra changes at distance at most \(43\) |
|---:|---:|---:|
| \(2\) | \(43\) | \(0\) |
| \(4\) | \(38\) | \(5\) |
| \(5\) | \(32\) | \(11\) |
| \(6\) | \(35\) | \(8\) |

This is an exact reduction to four bounded-extra cases. It is not, by itself, a proof that those cases are unsatisfiable.

The earlier judgment also supports the conditional observation that, if the universal labeled radius-\(43\) theorem were established without label-symmetry breaking, then the quantified labeled result would imply

\[
\min_{\pi\in S_6}d_H(\pi\circ C,B)\ge44.
\]

That consequence remains conditional because the radius-\(43\) theorem is not established by the supplied evidence.

### Radius-\(60\) decomposition

Color \(1\) is directly excluded at radius \(60\) because \(b_1=64\). The remaining cases are:

| \(C(537)\) | \(b_c\) | Maximum extra changes at distance at most \(60\) |
|---:|---:|---:|
| \(2\) | \(43\) | \(17\) |
| \(3\) | \(55\) | \(5\) |
| \(4\) | \(38\) | \(22\) |
| \(5\) | \(32\) | \(28\) |
| \(6\) | \(35\) | \(25\) |

Together with the direct color-\(1\) exclusion, these five cases exhaust all possible labeled colors of \(537\).

The latest judgment supports this finite case reduction and its exact distance accounting. It does not support the asserted unsatisfiability of the five cases because their LRAT proof payloads are absent.

### Scope

The decomposition concerns distance from one fixed labeled baseline on the first \(536\) positions. It does not imply the nonexistence of a distant or structurally unrelated coloring through \(537\), and it does not change the interval for \(S(6)\).

### Provenance

- **Primary judgments:**
  - `sha256:cc7d422e52197a8590621c4590d68e27e5bb4231ec4a155fdff8eca67ffc550b`
  - `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1`
- **Transactions:**
  - baseline: `b28dd977ae39eb77989de8e60b63f7eacd8982d2`
  - radius-\(43\) analysis: `26a77f38a16f35641a8d8f0efe72132953af5d2e`
  - radius-\(60\) analysis: `6a72758caaeb34a56d8d55653c8a3184ffbbe65e`
- **Relevant claim keys:**
  - `fs536-distance-decomposition-for-537-extensions`
  - `radius-60/blocker-distance-decomposition`

## Change: programs/explicit-coloring-certificates/hamming-distance-decomposition-at-537

The stable decomposition node is augmented with the supported radius-\(60\) case split and the exact auxiliary-variable interpretation used by the new encoding. The earlier radius-\(43\) decomposition and its qualifications are retained unchanged.

## Node: programs/explicit-coloring-certificates/sat-lrat-radius-60-method

**Title:** Conditioned SAT encoding and RUP/LRAT replay method for the radius-\(60\) extension problem  
**Type:** Method  
**Parent:** `programs/explicit-coloring-certificates`  
**Status:** Encoding supported; decisive proof payloads absent

### Current knowledge

Primary judgment `sha256:f8d51a0852eb5c904f4ced22e6c60aeededf65f464dbafd0855503b96739a8e1` supports the soundness and completeness of a finite reduction of the radius-\(60\) extension question to five conditioned CNFs.

For each

\[
c\in\{2,3,4,5,6\},
\]

the corresponding formula is satisfiable exactly when there is a labeled six-coloring \(C\) of \(\{1,\ldots,537\}\) such that:

- \(C(537)=c\);
- every integer receives exactly one of six labeled colors;
- no monochromatic solution of \(x+y=z\) occurs, including \(x=y\); and
- the restriction to \(1,\ldots,536\) has Hamming distance at most \(60\) from the fixed Fredricksen–Sweet baseline.

Color \(1\) is omitted from the SAT cases because its \(64\) blockers directly exclude it at radius \(60\).

### Coloring and Schur clauses

For every integer \(i\) and color \(c\), the variable \(X(i,c)\) denotes that \(i\) receives color \(c\). The formulas include:

- one at-least-one-color clause for every \(i\);
- all pairwise at-most-one-color clauses for every \(i\); and
- one Schur clause for every color and equation
  \[
  x+y=z,\qquad1\le x\le y,\qquad z\le537.
  \]

When \(x=y\), the encoding uses

\[
\neg X(x,c)\lor\neg X(2x,c),
\]

which the judgment accepts as the correct reduction of the duplicated three-literal prohibition.

The judgment supports the count

\[
\sum_{x=1}^{268}(538-2x)=268\cdot269=72{,}092
\]

for the unordered in-range Schur triples through \(537\), producing

\[
6\cdot72{,}092=432{,}552
\]

color-specific Schur clauses.

### Radius encoding

The five exact blocker splits are:

| \(C(537)\) | Blockers \(b_c\) | Allowed extra changes |
|---:|---:|---:|
| \(2\) | \(43\) | \(17\) |
| \(3\) | \(55\) | \(5\) |
| \(4\) | \(38\) | \(22\) |
| \(5\) | \(32\) | \(28\
