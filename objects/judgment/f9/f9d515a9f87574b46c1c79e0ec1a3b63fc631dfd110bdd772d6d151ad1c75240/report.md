## `bssc-sum-capacity/uniform-receiver-curve-continuum-bridge`

**Verdict: valid, within the claim’s expressly premise-bound and relaxed-system scope.**

### Required dependencies

1. **`e3c1036ca607539a5ebcddf3058e6014ac5c1cd9`** — required for the exact accepted 30-row system and its receiver-term structure.
2. **`e2bbc1e210e496b3c834e658820fc90287f3b2c0`** — required for the posterior-measure representation and sampled-curve reduction used and extended here.

Both are mathematical dependencies, not merely provenance citations. The external Gohari–Liu–Nair theorem itself remains an explicit premise of the first reference; its PDF authenticity or independent proof is not required for this claim, which only reasons from the resulting accepted row system.

### 1. Uniform continuity of binary-input receiver curves

For \(p\le p'\), let \(\delta=p'-p\). When \(\delta<1\), the proposed law

\[
R=\frac{(1-p')P_0+pP_1}{1-\delta}
\]

is a probability law and satisfies

\[
P_p=(1-\delta)R+\delta P_0,\qquad
P_{p'}=(1-\delta)R+\delta P_1.
\]

Introducing the mixture label \(E\), the exceptional component has deterministic \(X\). Hence

\[
H_{P_p}(X)=(1-\delta)H_R(X)+I_{P_p}(X;E),
\]

and similarly for \(P_{p'}\). Each correction lies in
\([0,H(E)]=[0,h_2(\delta)]\), so their difference has magnitude at most
\(h_2(\delta)\). The same chain-rule calculation conditional on \(A\) gives

\[
H_{P_p}(X\mid A)
=(1-\delta)H_R(X\mid A)+I_{P_p}(X;E\mid A),
\]

with \(0\le I(X;E\mid A)\le H(E)\). Therefore

\[
|H_{P_p}(X)-H_{P_{p'}}(X)|\le h_2(\delta),
\quad
|H_{P_p}(X\mid A)-H_{P_{p'}}(X\mid A)|\le h_2(\delta),
\]

and subtraction yields

\[
|J_A(p)-J_A(p')|\le 2h_2(|p-p'|).
\]

The exceptional case \(\delta=1\) is correctly handled: both priors are deterministic and both mutual informations vanish. The proof uses only the binary input, so it remains valid for arbitrary finite or generalized output alphabets.

### 2. Posterior-measure completion, compactness, and approximation

For a probability measure \(m\) on \([0,1]\) with mean \(1/2\), the measures

\[
dT_{A|0}=2(1-\rho)\,dm,\qquad dT_{A|1}=2\rho\,dm
\]

are nonnegative and each has total mass one. Under the fair prior, the output law is \(m\) and the posterior is \(\rho\). The integral formula for \(J_m(p)\) follows from direct substitution into mutual information. Atomic measures correspond to finite-output receivers after merging or splitting equal-posterior outputs.

The set \(\mathcal M_{1/2}\) is weakly compact because it is a closed subset of the probability measures on compact \([0,1]\). For fixed \(p\), continuity of the integrand gives pointwise convergence \(J_{m_n}(p)\to J_m(p)\) under weak convergence. The common modulus from part 1 upgrades this pointwise convergence to uniform convergence by a finite-net argument. Thus the image in \(C([0,1])\) is compact.

For an \(N\)-point grid \(Q\) containing \(0,1/2,1\), the map

\[
\rho\mapsto
\bigl(\rho,\psi(q_1,\rho),\ldots,\psi(q_{N-2},\rho)\bigr)
\in\mathbb R^{N-1}
\]

is continuous with compact image. Its \(m\)-barycenter lies in that image’s convex hull. Carathéodory’s theorem therefore supplies at most \(N\) atoms preserving the mean and all nonendpoint sampled curve values; the endpoint values are universally zero. This proves the exact grid match.

For any \(p\), selecting \(q\in Q\) with \(|p-q|\le\Delta_Q\) gives

\[
|J_m(p)-J_{m_Q}(p)|
\le 2h_2(|p-q|)+2h_2(|p-q|)
\le 4h_2(\Delta_Q).
\]

Because \(Q\) contains the endpoints, \(\Delta_Q\le1/2\), so the invoked monotonicity of \(h_2\) is applicable. Since both curve values lie in \([0,1]\), the bound can be replaced by

\[
\min\{1,4h_2(\Delta_Q)\}.
\]

The reflected construction is also correct:

\[
J_{m_Q^\circ}(p)=J_{m_Q}(1-p).
\]

If \(Q\) is reflection closed, exact matching of \(m_Q\) to \(m\) on \(Q\) implies exact matching of \(m_Q^\circ\) to \(m^\circ\) there, with the same uniform error. This preserves an already reflected pair but does not symmetrize arbitrary receiver pairs, exactly as qualified.

The grids \(Q_M=\{j/(2M):0\le j\le2M\}\) have \(2M+1\) points, are reflection closed, and have mesh radius \(1/(4M)\), so the error tends to zero. Consequently finite-output curves are uniformly dense in the compact generalized curve space.

### 3. Stability of all 30 rows

For every \(S-X-A\),

\[
I(S;A)=J_A(q)-\mathbb E J_A(q_S),\qquad
I(X;A\mid S)=\mathbb E J_A(q_S).
\]

Thus a sup-norm perturbation of \(J_A\) by at most \(\varepsilon_A\) changes:

- `W`, `UW`, `VW`, `U|W`, and `V|W` terms by at most \(2\varepsilon_A\);
- `X|UW` and `X|VW` terms by at most \(\varepsilon_A\).

For the conditional terms, for example,

\[
I(U;A\mid W)
=\mathbb E J_A(q_W)-\mathbb E J_A(q_{U,W}),
\]

so the asserted \(2\varepsilon_A\) bound is justified.

Direct comparison of the subject’s row generator with the declared reference’s accepted path-row generator shows the same 30 signed raw rows. Combining identical atoms and summing absolute signed multiplicities with the above weights produces exactly the displayed \((a_r,b_r)\) table. In particular, every coefficient satisfies

\[
a_r\le4,\qquad b_r\le4.
\]

Hence every row right side changes by at most

\[
a_r\varepsilon_G+b_r\varepsilon_K
\le4\varepsilon_G+4\varepsilon_K.
\]

This includes the four rate-free side-condition rows.

### 4. Feasibility consequences

If an original row is

\[
\ell_r(R_1,R_2)\le L_r(H;G,K)
\]

and \(|L_r(H;G',K')-L_r(H;G,K)|\le\eta_r\), then original feasibility implies

\[
\ell_r(R_1,R_2)\le L_r(H;G',K')+\eta_r.
\]

Thus the same rates and hierarchy are feasible for the explicitly relaxed approximating system. The reverse direction follows symmetrically.

For a fixed witness having positive slack in every row, finiteness of the 30-row collection gives a positive minimum after normalizing by the relevant coefficients. Since the grid approximation errors tend to zero, all row perturbations eventually become smaller than their corresponding slacks. Therefore strictly feasible witnesses persist under sufficiently fine approximation. No assumption about inactive rate-free constraints is silently introduced.

### Objective-attestation scope

The subject attestation establishes that the pinned no-argument Python execution:

- checked the exact declared dependency list;
- regenerated all 30 coefficient pairs and the global \((4,4)\) bound;
- checked the stated uniform-grid formulas for the tested range.

It does **not** computationally prove the entropy argument, Carathéodory reduction, compactness, or arbitrary-grid theorem; those obligations are instead established by the mathematical arguments above. The reference attestations likewise establish the encoded 30-row algebra, not the authenticity or independent truth of the external manuscript theorem.

### Scope qualification

The evidence does **not** establish unrelaxed convergence of \(B(G,K)\), a fixed cardinality for the full functional, reflected optimality, minimax interchange, a numerical improvement to the capacity interval, or the exact sum-capacity. The claim correctly disclaims all of these.
