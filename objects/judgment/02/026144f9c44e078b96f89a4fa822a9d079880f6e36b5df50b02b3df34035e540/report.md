## `bssc-sum-capacity/two-letter-marton-full-support-necessity`

**Verdict: valid**

**Required dependencies:** none. No reference transactions were declared, and the supplied contribution contains the necessary argument.

### 1. One-letter support inequalities

For \(q=\Pr[X=1]\), the stated formulas are correct:

\[
I_Y(q)=h_2((1-q)/2)-(1-q),\qquad
I_Z(q)=h_2(q/2)-q.
\]

Thus \(g(q)=I_Z(q)-I_Y(q)\) satisfies

\[
g''(q)=\frac{2q-1}{\ln 2\,q(1-q)(1+q)(2-q)}.
\]

Hence \(g\) is concave on \((0,\frac12)\) and convex on \((\frac12,1)\). The identities

\[
g(1/5)=\frac85r,\qquad g'(1/5)=-2r,\qquad
r=h_2(1/4)-\frac34>0
\]

make the tangent at \(1/5\) equal to \(2r(1-q)\). Concavity gives the bound on \([0,\frac12]\); on \([\frac12,1]\), convexity together with \(g(1/2)=g(1)=0\) gives \(g(q)\le0\). Reflection \(g(1-q)=-g(q)\) then gives, including endpoints by continuity,

\[
g(q)\le2r(1-q),\qquad -g(q)\le2rq.
\]

These inequalities are correctly applied to posterior input distributions later in the proof.

### 2. Product-channel identity and Marton reduction

The chain-rule identity

\[
\begin{aligned}
I(S;Y^2\mid C)-I(S;Z^2\mid C)
={}&I(X_1;Y_1\mid C,Z_2)-I(X_1;Z_1\mid C,Z_2)\\
&+I(X_2;Y_2\mid C,Y_1)-I(X_2;Z_2\mid C,Y_1)
\end{aligned}
\]

is valid for the memoryless product coupling. Conditional on each displayed conditioning variable, the remaining coordinate retains the governed one-letter marginal channel. Averaging the one-letter support inequalities therefore correctly yields

\[
I(S;Y^2\mid C)-I(S;Z^2\mid C)\le 2r(q_1+q_2),
\]

and, after exchanging receivers,

\[
I(S;Z^2\mid C)-I(S;Y^2\mid C)
\le 2r(2-q_1-q_2).
\]

The Marton reduction is also valid. With \(A=(W,U)\),

\[
\begin{aligned}
M
&\le I(A;Y^2)+I(V;Z^2\mid W,U)-I(U;V\mid W,Z^2)\\
&\le I(A;Y^2)+I(S;Z^2\mid A),
\end{aligned}
\]

where the last step uses nonnegativity and conditional data processing. The symmetric bound with \(B=(W,V)\) is analogous. Combining these with the preceding inequalities and averaging gives the central universal estimate

\[
M\le G(P_S)+2r,\qquad
G(P_S)=\frac{I(S;Y^2)+I(S;Z^2)}2.
\]

No unproved additivity or external binary-input Marton theorem is used here.

### 3. Maximization over the three-symbol faces

The concavity of \(G\) in \(P_S\) and its invariance under coordinate transposition and complemented receiver reflection justify the symmetrizations. The four faces split into the two claimed orbits.

#### Missing \(00\) or \(11\)

After symmetrization,

\[
P(01)=P(10)=s,\qquad P(11)=1-2s.
\]

The supplied output laws, row entropies, and resulting formulas

\[
I(S;Y^2)=h_2(s)-s
\]

and

\[
I(S;Z^2)
=H_4\!\left(\frac{1+2s}{4},\frac14,\frac14,\frac{1-2s}{4}\right)-2+2s
\]

are correct. The second derivative is strictly negative on \(0<s<1/2\), and \(s=2/5\) is the unique stationary point. Therefore

\[
\max_{\mathcal F_{\rm end}}G
=\frac34\log_2\frac53.
\]

Consequently,

\[
M\le 0.675280444542921\ldots<0.695.
\]

#### Missing \(01\) or \(10\)

After the valid endpoint symmetrization,

\[
P(00)=P(11)=\frac{1-s}{2},\qquad P(10)=s.
\]

The output law and conditional entropy calculation give

\[
G(s)=H_4\!\left(\frac{1-s}{8},\frac{1-s}{8},
\frac{1+3s}{8},\frac{5-s}{8}\right)-1.
\]

Its displayed second derivative is negative. At \(s_0=1/6\),

\[
G'(s_0)=\frac18\log_2\frac{725}{729}<0.
\]

The global tangent bound for a concave function, together with
\(s\in[0,1]\), correctly gives

\[
G(s)\le G(s_0)-\frac16G'(s_0)
=0.572001729864294\ldots.
\]

Thus

\[
M\le 0.694557978782560\ldots<0.695.
\]

Every law supported on at most three symbols belongs to at least one of these faces, so the headline bound \(M<0.695\) follows.

### 4. Explicit randomized-time-division witness

The described fair schedule can be realized as a finite Marton law: in one state \(V=X\) and \(U\) is constant with input prior \(q\), while in the reflected state \(U=X\) and \(V\) is constant with input prior \(1-q\). For \(J(q)=h_2(q/2)-q\), both common terms equal

\[
J(1/2)-\frac{J(q)+J(1-q)}2,
\]

and the sum of private terms is \(J(q)\). Independent repetition twice therefore doubles the one-letter value. At \(q=1/6\), this is exactly

\[
B_{1/6}
=2h_2(1/4)+h_2(1/12)-h_2(5/12)-\frac13
=0.723171009237413\ldots>0.7231.
\]

Thus any strict improvement over twice the optimal one-letter RTD value also exceeds this explicit \(B_{1/6}\), since the optimum is at least the value at \(q=1/6\).

### 5. Quantitative mass floors

For \(m=P_S(x)<1\) and \(Q=P_{S\mid S\ne x}\), the indicator decomposition gives, for either receiver output \(O\),

\[
I(S;O)\le h_2(m)+(1-m)I_Q(S;O).
\]

Hence

\[
G(P_S)\le h_2(m)+(1-m)G(Q).
\]

Removing \(00\) or \(11\) places \(Q\) on an end face; removing \(01\) or \(10\) places it on a mixed face. The corresponding certified bounds therefore apply.

For \(\phi_C(m)=h_2(m)+(1-m)C\),

\[
\phi_C'(m)=\log_2\frac{1-m}{m}-C.
\]

The checker verifies positivity of this derivative through the relevant intervals and certifies

\[
\phi_{C_{\rm end}}(1/180)+2r<B_{1/6},
\]

\[
\phi_{C_{\rm mixed}}(1/325)+2r<B_{1/6}.
\]

Therefore any law with \(M>B_{1/6}\), and hence any strict improvement over twice the optimal one-letter RTD benchmark, must satisfy

\[
P_S(00),P_S(11)>\frac1{180},\qquad
P_S(01),P_S(10)>\frac1{325}.
\]

The inequalities are correctly strict, including at the threshold values.

### 6. Objective-attestation audit

The supplied terminal attestation records successful execution with exit code \(0\) of the configured no-argument `verify.py` checker under the pinned Python verifier. The checker:

- verifies the product-channel symmetries and the two face orbits in exact `Fraction` arithmetic;
- verifies the affine output distributions and row entropies;
- uses outward-expanded 80-digit decimal intervals for logarithmic quantities;
- certifies the numerical face bounds, \(B_{1/6}>0.7231\), and both mass-floor separations.

The attestation supports the finite algebraic and numerical inequalities only; it does not by itself prove the universal Marton reduction or calculus arguments. Those obligations are, however, supplied and valid in the written proof.

### Scope

The conclusion is correctly limited to the unnormalized two-letter Marton functional. It neither proves a full-support no-gain theorem nor gives a converse for unrestricted broadcast coding or alter the stated capacity interval.
