# Render-complete Theorem 9 private-message row audit

## Claim and exact scope

The committed primary-source PDF and the structured transcription in
`theorem9_spec.json` agree exactly on the factorization, equations
(19a)--(19p), and
both side conditions of Gohari--Liu--Nair Theorem 9.  The no-argument verifier
reads the PDF itself and fail-closes over the complete rendering envelope:
page-tree order and boxes, single content streams, the exhaustive operator
census, recursive resources, text/graphics state, embedded Type1 encodings and
decrypted CharStrings, ToUnicode agreement, glyph positions, clipping, color,
and every possible painting operation.  It then compares the complete visible
mathematical statement with `theorem9_spec.json`.  After the private-message specialization
$R_0=0$, expanding every displayed minimum produces 26 scalar rows and
splitting the two interval side conditions produces four more; these are
exactly, term for term, the local 30-row formulation independently generated
by the generic $L=3$ path formulas in `verify_specialization.py`.

Taking the cited Theorem 9 as a primary-source premise, the exhaustive term
audit also proves that input-only product marginalization of $G,K$ preserves
the entire system.  Under the explicit extended-real definitions below,

\[
V_Q(G,K)\le V(1/2;G,K)\le B(G,K),
\]

and on $Q_0=\{0,1/2,1\}$ every row depends on the four receiver channels only
through $(c,g,k,c)$; hence $V_0(g,k)$ is well defined.  The source binding,
source equivalence, marginalization, and $Q_0$ reduction form one
all-or-nothing foundation claim.

This contribution does **not** re-prove Theorem 9 itself and does **not**
claim a numerical capacity bound, the optimum of the $Q_0$ problem, a
coercive inequality, a receiver-cardinality theorem, or a continuum limit.

## Primary-source boundary

The primary source is:

> Amin Gohari, Yi Liu, and Chandra Nair, *A Two Auxiliary Receiver Outer Bound
> to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast
> Channel*, Appendix B, Theorem 9, equations (19a)--(19p).

Official manuscript:
<https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf>

The exact reviewed manuscript is committed as `GK-outer.pdf`.  It has 255268
bytes, embedded creation date 2026-01-14, and SHA-256
`24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa`.
`SOURCE_TRANSCRIPTION.md` is a human-readable rendering for review;
`theorem9_spec.json` is the authoritative machine-bound transcription of the
complete factorization, source equations, and side conditions.
`pdf_source_extract.py` is a deliberately strict standard-library rendering
audit for the pinned Appendix B pages.  It binds the terminal `startxref`
through both xref streams, verifies every direct/compressed object resolution,
and binds the exact catalog to page-tree root 145, then
proves that objects 29 and 31 are PDF pages 14 and 15 in page-tree order, each
has exactly one content stream,
the exact effective MediaBox/CropBox `[0 0 612 792]`, no inherited CropBox,
rotation, MediaBox, or Resources override, and no annotations or alternate
appearance stream.  It parses every content token and accepts only the exact
observed operators: balanced `BT`/`ET`, positive `Tf`, paired `Td`/`TJ`, and
the black/color-setting `g`/`G`/`rg`/`RG` operations.  Legal alternatives such
as `Tj`, `'`, `"`, `Do`, text-rendering changes, transformations, clipping,
graphics-state changes, paths, images, transparency, and optional content are
handled or rejected explicitly; no unknown operator is discarded.

The audit recursively resolves the full resource closure and proves that
there is no Form, Image, or other XObject and that the referenced ExtGState is
empty.  The page resource and simple-font dictionaries must match the exact
reviewed, duplicate-free profile.  For every theorem glyph the audit resolves
the operative PDF or embedded Type1 Encoding, requiring exactly one embedded
Encoding definition, rejecting duplicate or unrecognized direct/inline PDF
Encoding override, and permitting only the pinned indirect Differences
object.  It requires the glyph in both the exact FontDescriptor `CharSet` and
the uniquely declared decrypted embedded `CharStrings` dictionary, then checks
each complete decoded font program against a reviewed per-font SHA-256
manifest.  Its bounded glyph-name-to-Unicode interpretation must also equal an
exhaustively parsed, one-byte, non-inherited ToUnicode CMap.  It tracks the
cumulative `Td` anchors, positive font widths and bounding boxes, requires
left-to-right order on unchanged baselines, and binds the complete reviewed
1,789-glyph order and layout to digest
`43e10353f3dade58020fde708193bdf3d1114df7cd84fbc54359aec0aa2bcef0`.
Every theorem glyph is opaque black, strictly inside the page, and cannot be
covered by pre-Appendix content.  Because `TJ` is the only painting operator,
this also excludes an unparsed or later overlay with different visible
content.  The verifier then generates the source-facing equations,
factorization, and side conditions from the structured term spec and compares
them with the complete visible source text.  Thus neither a citation nor a
second hard-coded row list stands in for source fidelity.

The earlier transactions
`d638c346212db3e75f6a53dcebcfd09f55125852`,
`f093396fe03f8920f9905c385ef34b1335792d5e`, and
`dcdd3ab29be1a45b42a75767dbee30d8381544eb` motivated this render-complete
replacement, but the proof and artifacts here do not use any of them as a
mathematical premise.  They are provenance references, not declared claim
dependencies.

## Definitions and optimization order

Fix the physical BSSC $T_{Y,Z|X}$.  After the marginalization proved below,
fix finite-output binary-input channels $T_{G|X}$ and $T_{K|X}$.  For
$q\in[0,1]$, use $P(X=1)=q$.

Define $V(q;G,K)$ to be the extended-real supremum of $R_1+R_2$ over:

1. nonnegative $R_1,R_2$;
2. finite auxiliary triples
   $(U_j,V_j,W_j)$, $j\in\{a,b,c\}$, with conditional law
   \[
   p_{U_a,V_a,W_a|X}p_{U_b,V_b,W_b|X}p_{U_c,V_c,W_c|X};
   \]
3. choices satisfying all 26 private-rate/nonnegativity rows obtained from
   (19a)--(19p) after setting $R_0=0$, and all four scalar inequalities
   obtained from the two side conditions.

Thus the supremum over rates and finite auxiliary hierarchies is taken while
$q,G,K$ are fixed.  No closure or attainment is assumed.  Throughout this
contribution, $\sup\varnothing=-\infty$; this makes every restricted value
defined even when a support restriction admits no feasible hierarchy.

Define the fixed-receiver full-prior value by

\[
B(G,K):=\sup_{q\in[0,1]}V(q;G,K).
\]

This order is important: first optimize the Theorem 9 auxiliary hierarchy at
fixed $q,G,K$, then take the supremum over $q$.  The resulting receiver
outer bound is subsequently minimized over finite $G,K$:

\[
C_{\rm sum}\le \inf_{G,K}B(G,K).
\]

No equality or interchange with
$\sup_q\inf_{G,K}V(q;G,K)$ is asserted.

For a fixed receiver $A\in\{Y,G,K,Z\}$, let

\[
J_A(t):=I(X;A)\quad\text{when }P(X=1)=t
\]

with $T_{A|X}$ held fixed.  Let $Q\subset[0,1]$ be finite and contain
$1/2$.  A fair-prior auxiliary hierarchy is **$Q$-supported** when every
positive-probability posterior

\[
P(X=1|W_j),\qquad P(X=1|U_j,W_j),\qquad
P(X=1|V_j,W_j)
\]

belongs to $Q$, for all three groups.  Define

\[
V_Q(G,K):=\sup\{R_1+R_2:\text{the defining optimization for }
V(1/2;G,K)\text{ uses a }Q\text{-supported hierarchy}\}.
\]

This is a restriction inside the auxiliary-hierarchy supremum, hence

\[
V_Q(G,K)\le V(1/2;G,K)\le \sup_qV(q;G,K)=B(G,K).
\]

Finally let

\[
Q_0=\{0,1/2,1\},\qquad
c=J_Y(1/2)=J_Z(1/2)=h_2(1/4)-1/2.
\]

For any $G,K$, put $g=J_G(1/2)$, $k=J_K(1/2)$, and define

\[
V_0(g,k):=V_{Q_0}(G,K).
\]

The proof below shows that the right-hand side depends only on $g,k$, not on
which channels realize those two midpoint values, so this definition is
unambiguous.  It is also a finite real value: the $Q_0$-supported choice
$W_a=W_b=W_c=X$ with all $U_j,V_j$ constant makes both side conditions zero
and admits $R_1=R_2=0$, while the branch-zero individual-rate rows give
$R_1\le I(U_a,W_a;Y)\le1$ and
$R_2\le I(V_c,W_c;Z)\le1$.

## Exact expansion to 30 rows

In the source, (19c)--(19d), (19e)--(19f), (19g)--(19h), and
(19i)--(19j) are four inequalities whose continuations carry separate equation
labels.  Expanding a condition $L\le A+\min\{b_1,\ldots,b_m\}$ means imposing
the $m$ scalar rows $L\le A+b_i$.  The complete mapping is:

| source line(s) | branches | generated local rows |
|---|---:|---|
| (19a) | 3 | `N_Y(0)`, `N_Y(1)`, `N_Y(2)` |
| (19b) | 3 | `N_Z(0)`, `N_Z(1)`, `N_Z(2)` |
| (19c)--(19d) | 3 | `R1T(0)`, `R1T(1)`, `R1T(2)` |
| (19e)--(19f) | 3 | `R1A(0)`, `R1A(1)`, `R1A(2)` |
| (19g)--(19h) | 3 | `R2A(0)`, `R2A(1)`, `R2A(2)` |
| (19i)--(19j) | 3 | `R2T(0)`, `R2T(1)`, `R2T(2)` |
| (19k) | 2 | `SL(3,U)`, `SL(3,C)` |
| (19l) | 2 | `SR(1,C)`, `SR(1,U)` |
| (19m) | 1 | `SL(2,U)` |
| (19n) | 1 | `SL(1,U)` |
| (19o) | 1 | `SR(2,U)` |
| (19p) | 1 | `SR(3,U)` |

These are 26 rows.  Each side condition $0\le L\le R$ is exactly the pair
$L\ge0$, $R-L\ge0$.  The $Z,K$ condition gives `F_Z_left` and
`F_Z_right_minus_left`; the $Y,G$ condition gives `F_Y_left` and
`F_Y_right_minus_left`.  The total is therefore 30.

Before constructing rows, the verifier authenticates `GK-outer.pdf`, extracts
the complete theorem statement from source pages 14--15, and checks all 16
equation labels, the factorization, and both side conditions against the
structured term spec.  It then constructs rows in two independent ways.
First, it reads `theorem9_spec.json`, expands every minimum, and splits the
side conditions.  Second, `make_path_rows` builds an $L=3$ chain
$Y\to G\to K\to Z$ from generic left- and right-walk formulas.
It normalizes the results only with

\[
I(U,W;A)=I(W;A)+I(U;A|W),\qquad
I(V,W;A)=I(W;A)+I(V;A|W),
\]

and compares the rate coefficients and every signed information term exactly.

## Exhaustive output-term audit and marginalization

The complete distinct output-bearing term set from the source transcription is:

| output | terms |
|---|---|
| $Y$ | $I(W_a;Y)$, $I(U_a;Y|W_a)$, $I(X;Y|V_a,W_a)$ |
| $Z$ | $I(W_c;Z)$, $I(V_c;Z|W_c)$, $I(X;Z|U_c,W_c)$ |
| $G$ | $I(W_a;G)$, $I(W_b;G)$, $I(U_a,W_a;G)$, $I(U_b,W_b;G)$, $I(V_a,W_a;G)$, $I(V_b,W_b;G)$, $I(U_a;G|W_a)$, $I(U_b;G|W_b)$, $I(V_b;G|W_b)$, $I(X;G|U_a,W_a)$, $I(X;G|V_a,W_a)$, $I(X;G|V_b,W_b)$ |
| $K$ | $I(W_b;K)$, $I(W_c;K)$, $I(U_b,W_b;K)$, $I(U_c,W_c;K)$, $I(V_b,W_b;K)$, $I(V_c,W_c;K)$, $I(U_b;K|W_b)$, $I(V_b;K|W_b)$, $I(V_c;K|W_c)$, $I(X;K|U_b,W_b)$, $I(X;K|U_c,W_c)$, $I(X;K|V_c,W_c)$ |

The verifier compares this 3/12/12/3 audit against a second, independently
encoded whitelist.  In particular, there is no joint $(G,K)$ output term and
no term that conditions one output on another.

For an arbitrary admitted $T_{G,K|X,Y,Z}$, define

\[
\bar T_{G|X}(g|x)=\sum_{y,z,k}T_{Y,Z|X}(y,z|x)
T_{G,K|X,Y,Z}(g,k|x,y,z),
\]

\[
\bar T_{K|X}(k|x)=\sum_{y,z,g}T_{Y,Z|X}(y,z|x)
T_{G,K|X,Y,Z}(g,k|x,y,z),
\]

and replace it by

\[
T'_{G,K|X,Y,Z}(g,k|x,y,z)=\bar T_{G|X}(g|x)\bar T_{K|X}(k|x).
\]

If $D$ is any subtuple of one auxiliary group, then the Theorem 9
factorization gives

\[
p(d,x,g)=p_X(x)p_{D|X}(d|x)\bar T_{G|X}(g|x).
\]

This law is unchanged by $T'$, and the same calculation holds for $K$.
The $Y,Z$ laws are unchanged directly.  The exhaustive term audit therefore
shows that every row and both side conditions are preserved term by term.  The
reverse inclusion is immediate because an input-only product channel is an
allowed $T_{G,K|X,Y,Z}$.

## Why $V_0(g,k)$ is well defined

For any Markov chain $S-X-A$, posterior conditioning and the chain rule give

\[
I(S;A)=J_A(1/2)-\mathbb E[J_A(q_S)],\qquad
I(X;A|S)=\mathbb E[J_A(q_S)],
\]

where $q_S=P(X=1|S)$.  In particular,

\[
I(U;A|W)=\mathbb E[J_A(q_W)]-\mathbb E[J_A(q_{U,W})],
\]

with the analogous $V$ identity.  These identities cover every term kind in
the audited system: `W`, `U|W`, `V|W`, `UW`, `VW`, `X|UW`, and `X|VW`.

For $Q_0$-supported hierarchies, $J_A(0)=J_A(1)=0$; hence all these
expectations use only $J_A(1/2)$.  The physical BSSC values are $c,c$, and
the auxiliary-receiver values are $g,k$.  Therefore every objective row and
feasibility row is determined by the four scalar values $(c,g,k,c)$, proving
that $V_{Q_0}(G,K)$ depends on $G,K$ only through $g,k$.

## Reproduction

From this contribution directory, the repository-bounded check is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_specialization.py
```

`verification.json` requests that exact no-argument entrypoint in the governed
`python-stdlib-3-13-v1` environment, pinned at verifier-spec digest
`sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884`.
The governed runner invokes `python3 -I -B verify_specialization.py`; the
extractor is loaded by its exact sibling path and does not rely on ambient
module search paths.  The trusted attestation therefore covers the committed
PDF bytes, its complete render/semantic comparison with the structured source spec, the
independent path-row comparison, and the exhaustive term audit.  It makes no
network request.

A reviewer can independently redownload the public author-hosted bytes and
compare their digest with the committed source:

```bash
curl -fsS https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf \
  -o /tmp/GK-outer.pdf
shasum -a 256 /tmp/GK-outer.pdf GK-outer.pdf
```

The checker uses only the Python standard library, exact integer linear forms,
zlib and Type1 decoding, operative font encodings, embedded CharStrings and
ToUnicode maps, and SHA-256.  It first emits the exact
page/operator/resource/glyph-geometry audits, then one `PASS` line for every
source equation and source branch/side-condition row, authenticates
the factorization and exhaustive term audit, and finishes with:

```text
PASS: committed primary source, factorization, (19a)-(19p), both side conditions, and all 30 private-message rows agree exactly
```

## Limitations and authorship

- This audit uses Theorem 9 as a primary-source premise; it does not re-prove
  the coding-theorem converse behind Theorem 9.
- The official URL is mutable.  The committed PDF bytes, byte length, SHA-256,
  embedded creation date, page location, and render-complete semantic audit
  pin the reviewed version.  The author-host URL is source provenance; the
  networkless verifier authenticates the committed reviewed bytes rather than
  making a mutable network request.
- No assertion is made about a $Q_0$ optimum, midpoint coercivity, receiver
  cardinality, continuum convergence, reflected optimality, or a numerical
  capacity upper bound.
- The mathematical theorem and equations are attributed to Gohari, Liu, and
  Nair.  The independent transcription audit, definitions, path comparison,
  and verifier in this contribution were prepared for Math Flow.
