# Bounded transcription of Gohari--Liu--Nair Theorem 9

This file is a human-readable display of the mathematical premise.  The
authoritative exact premise is encoded in `theorem9_spec.json`.  The displayed
statement is attributed to Amin Gohari, Yi Liu, and Chandra Nair, *A Two Auxiliary Receiver Outer Bound
to the Capacity Region of a Two-Receiver Discrete Memoryless Broadcast
Channel*, Appendix B, Theorem 9, PDF pages 14--15:

<https://chandra.ie.cuhk.edu.hk/pub/papers/BC/GK-outer.pdf>

For bibliographic provenance, the version consulted had 255268 bytes and
SHA-256
`24c4153530008f7ae339ac19ca8cb90fb8ea574ea8fbcd6a36c2221722d651fa`.
Neither that provenance nor fidelity to external PDF rendering is part of the
claim.  `theorem9_spec.json` is this premise in executable form, and
`verify_specialization.py` checks only its downstream mathematical
specialization and reductions.

## Factorization and quantifiers

For a broadcast channel $T_{Y,Z|X}$ and an achievable rate triple, Theorem 9
states that there is an input law $p_X$ such that, for every auxiliary channel
$T_{G,K|X,Y,Z}$, the constraints below hold for some finite auxiliary laws
with joint factorization

\[
p_X p_{U_a,V_a,W_a|X} p_{U_b,V_b,W_b|X}
p_{U_c,V_c,W_c|X} T_{Y,Z|X} T_{G,K|X,Y,Z}.
\]

## Equations (19a)--(19p)

\[
\begin{aligned}
R_0\le{}&I(W_a;Y)+\min\{0,
 I(W_b;G)-I(W_a;G),\\
&I(W_b;G)-I(W_a;G)+I(W_c;K)-I(W_b;K)\}. \tag{19a}
\end{aligned}
\]

\[
\begin{aligned}
R_0\le{}&I(W_c;Z)+\min\{0,
 I(W_b;K)-I(W_c;K),\\
&I(W_b;K)-I(W_c;K)+I(W_a;G)-I(W_b;G)\}. \tag{19b}
\end{aligned}
\]

The source places labels (19c) and (19d) on the two displayed lines of this
single inequality:

\[
\begin{aligned}
R_0+R_1\le{}&I(W_a;Y)+I(U_a;Y|W_a) \tag{19c}\\
&+\min\{0,
 I(U_b,W_b;G)-I(U_a,W_a;G),\\
&\qquad I(U_b,W_b;G)-I(U_a,W_a;G)
 +I(U_c,W_c;K)-I(U_b,W_b;K)\}. \tag{19d}
\end{aligned}
\]

Likewise, (19e) and (19f) are one inequality:

\[
\begin{aligned}
R_0+R_1\le{}&I(W_c;Z)+I(U_a;Y|W_a)
 +I(W_a;G)-I(W_b;G)+I(W_b;K)-I(W_c;K) \tag{19e}\\
&+\min\{0,
 I(U_b,W_b;G)-I(U_a,W_a;G),\\
&\qquad I(U_b,W_b;G)-I(U_a,W_a;G)
 +I(U_c,W_c;K)-I(U_b,W_b;K)\}. \tag{19f}
\end{aligned}
\]

Equations (19g) and (19h) are one inequality:

\[
\begin{aligned}
R_0+R_2\le{}&I(W_a;Y)+I(V_c;Z|W_c)
 +I(W_c;K)-I(W_b;K)+I(W_b;G)-I(W_a;G) \tag{19g}\\
&+\min\{0,
 I(V_b,W_b;K)-I(V_c,W_c;K),\\
&\qquad I(V_b,W_b;K)-I(V_c,W_c;K)
 +I(V_a,W_a;G)-I(V_b,W_b;G)\}. \tag{19h}
\end{aligned}
\]

Equations (19i) and (19j) are one inequality:

\[
\begin{aligned}
R_0+R_2\le{}&I(W_c;Z)+I(V_c;Z|W_c) \tag{19i}\\
&+\min\{0,
 I(V_b,W_b;K)-I(V_c,W_c;K),\\
&\qquad I(V_b,W_b;K)-I(V_c,W_c;K)
 +I(V_a,W_a;G)-I(V_b,W_b;G)\}. \tag{19j}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&\min\{I(W_a;Y),
 I(W_c;Z)+I(W_a;G)-I(W_b;G)+I(W_b;K)-I(W_c;K)\}\\
&+I(U_c,W_c;K)-I(U_b,W_b;K)
 +I(U_b,W_b;G)-I(U_a,W_a;G)\\
&+I(U_a;Y|W_a)+I(X;Z|U_c,W_c). \tag{19k}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&\min\{I(W_a;Y)+I(W_c;K)-I(W_b;K)
 +I(W_b;G)-I(W_a;G), I(W_c;Z)\}\\
&+I(V_a,W_a;G)-I(V_b,W_b;G)
 +I(V_b,W_b;K)-I(V_c,W_c;K)\\
&+I(V_c;Z|W_c)+I(X;Y|V_a,W_a). \tag{19l}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_a;Y)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(U_b,W_b;G)-I(U_a,W_a;G)-I(V_c;K|W_c)
 +I(X;K|U_b,W_b). \tag{19m}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_a;Y)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(V_b;K|W_b)-I(V_c;K|W_c)-I(V_b;G|W_b)
 +I(X;G|U_a,W_a). \tag{19n}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_c;Z)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(V_b,W_b;K)-I(V_c,W_c;K)-I(U_a;G|W_a)
 +I(X;G|V_b,W_b). \tag{19o}
\end{aligned}
\]

\[
\begin{aligned}
R_0+R_1+R_2\le{}&I(W_c;Z)+I(U_a;Y|W_a)+I(V_c;Z|W_c)\\
&+I(U_b;G|W_b)-I(U_a;G|W_a)-I(U_b;K|W_b)
 +I(X;K|V_c,W_c). \tag{19p}
\end{aligned}
\]

## Both side conditions

\[
0\le I(X;Z|U_c,W_c)-I(X;K|U_c,W_c)
\le I(V_c;Z|W_c)-I(V_c;K|W_c),
\]

\[
0\le I(X;Y|V_a,W_a)-I(X;G|V_a,W_a)
\le I(U_a;Y|W_a)-I(U_a;G|W_a).
\]

No definition of $B(G,K)$, $V(q;G,K)$, $V_Q(G,K)$, or
$V_0(g,k)$ is attributed to the paper.  Those are explicit local definitions
given in `README.md`, derived from this complete constraint system.
