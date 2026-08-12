This assessment assigns credit to immutable transaction IDs rather than to author labels. It preserves the locked mathematical state and treats significance as qualitative and non-zero-sum.

## Contribution: dfc0cc40d41105292a119840dcdbe6f22860cf43

**Primary roles:** certificate reproduction, exact verification, baseline infrastructure, and concise exposition.

This transaction made the existing 152-point \(G_{76}\) record self-contained and independently checkable. Its durable contribution is not the original coordinate construction: the locked state attributes that construction to the maintained external database. Credit to this transaction instead attaches to preserving the coordinate payload, documenting its decoding, and supplying an exact-integer verifier that checks 152 distinct in-grid points and all \(573{,}800\) unordered triples. That work directly supports `g76/152-point-certificate` (revision `sha256:672237736db5cdd2e1b34ad069e13c9a905b5d43e9a824801630631abefaf384`) and thereby the certified lower bound in `d77/certified-interval` (revision `sha256:044564ce8112ae832398148b6df4f2477a715c25a8b75f9af95ab4d7e13cc917`).

Its causal value is larger than a mere restatement of the known bound. By committing the exact data and verifier, it gave later transactions a stable computational object rather than a claim dependent on a mutable source. Transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f` directly reused and independently decoded this certificate for its local-rigidity analysis, while transaction `c98dd877ad81611a9a469b1bd790cd909b56b1ce` reused the documented certificate convention in its calibration machinery. Thus this transaction enabled subsequent verification and search infrastructure even though it did not originate the record itself.

The elementary upper bound and the resulting occupancy observations also contributed to `d77/extremal-occupancy` (revision `sha256:8656144d79c90f0d1e89ea986ca8111e1d304c014a136fe916c3a17a073b0cd4`). Credit for those observations should be modest: they follow immediately from the two-points-per-row and two-points-per-column bounds. Their usefulness lies in clearly fixing the necessary occupancy patterns for hypothetical 153- and 154-point sets, not in mathematical depth.

The verifier’s treatment of the leading symmetry marker is a limited quality caveat. It recognizes the marker but does not verify the represented quarter-turn symmetry. The locked state explicitly records that this does not affect the no-three-in-line certificate, because the determinant checks depend only on the decoded coordinates. The omission was later repaired for this particular configuration by transaction `c5e8096d942d57228bb4fed00f7617fb6b43af9f`. Credit here should therefore remain high for certification, but not extend to symmetry verification.

No supplied research-direction registration predates or specifically supports this transaction. The only registered direction concerns the later finite-rotation proof, so it supplies no priority evidence here. Nor should the transaction receive construction priority merely because it was the first canonical ledger entry: the locked provenance distinguishes the prior coordinate construction from this transaction’s independent reproduction and verification.

**Qualitative significance:** foundational and enabling. It certified the lower endpoint and created the reusable baseline on which later work depended, but it neither improved the inherited interval nor originated the 152-point construction.

## Contribution: c5e8096d942d57228bb4fed00f7617fb6b43af9f

**Primary roles:** exhaustive local computation, verification, negative search result, structural census, and correction of a limited verification gap.

This transaction produced the main durable knowledge in the record-perturbation program. For each of the eight specified embeddings of the certified record, it established saturation, persistence of saturation after one removal, and a complete census through removal depth two. Those results are represented in:

- `g76/record-symmetry-and-g77-embeddings` (revision `sha256:320dec3eb81e8ada2724c8fee84673a9fcadad36e395bfac1f00ab052544fd65`);
- `d77/embedded-record-local-rigidity` (revision `sha256:543c00c7de49d5de319772336910a37b10658378ce58ad47cf53c5d52d581c3b`);
- `d77/distance-from-embedded-record` (revision `sha256:affda03b7697754e7e1139e2a6e37cd0ef69e40deacdb0061c029f0c3f9073b9`).

The exact distance consequence is particularly useful: any no-three-in-line set of size at least 153 must be at symmetric-difference distance at least seven from each specified embedding. This does not solve the global problem, but it converts a vague perturbative idea into a certified pruning rule. It tells future searches that deleting at most two points from any of these embeddings cannot yield an improvement and quantifies the minimum departure required.

The computational quality is strong within that scope. The contribution supplies deterministic standard-library code, exact integer arithmetic, committed expected output, exhaustive consideration of all outside cells, two structurally different enumerations, and direct simulation of every reported freeing. The line census and line-walk calculations are not completely independent—they share the decoded configuration and primitive-direction machinery—but they provide meaningful cross-checking rather than superficial duplication. The locked state also records the residual verification uncertainty accurately: confidence rests on source inspection and supplied deterministic results rather than on a separately documented execution environment. That is a modest reproducibility caveat, not a reason to erase the computational credit.

The transaction also independently verified that the baseline configuration is quarter-turn invariant, resolving the marker-verification limitation left by the first transaction. It then determined the two distinct dihedral images and eight distinct specified embeddings. This is a genuine corrective and classificatory contribution, although its scope is only the listed dihedral images and four natural translations—not arbitrary affine images or all 152-point configurations.

An important credit discount concerns the broad phrase that the computation “prunes the entire ‘perturb the known record’ strategy.” The locked state does not retain that breadth. `d77/record-perturbation-frontier` (revision `sha256:c51784ccf8bb4c9b3b142f993db084783f72d2a11b8bc6cdc647bce1fdcb3a41`) records that removal depth three and beyond, three-for-four replacements, deeper neighborhoods, other 152-point configurations, and unrelated constructions remain open. Credit should therefore attach to exhaustive local rigidity through depth two, not to abandonment of the broader perturbation program.

This transaction depends materially on `dfc0cc40d41105292a119840dcdbe6f22860cf43` for the base certificate. It deserves independent credit for the local analysis, code, symmetry check, and resulting corollary, but not for the underlying coordinates or the original 152-point construction.

No supplied direction registration predates this work. Its priority evidence comes from the canonical transaction and resulting knowledge revisions, not from a registered plan. Follow-through is nevertheless substantial: the contribution includes the complete code, exact output census, reproduction procedure, and clearly delimited negative conclusion.

**Qualitative significance:** substantial within a narrow neighborhood. It gives a rigorous and reusable local obstruction and search-pruning capability, while leaving the certified interval and all configurations outside the specified depth-two neighborhoods untouched.

## Contribution: c98dd877ad81611a9a469b1bd790cd909b56b1ce

**Primary roles:** restricted-model construction, implementation, calibration, bounded search, partial structural proof, and research-program formation.

The most durable contribution of this transaction is the exact \(n=77\) model for the strict `rct4` subclass. As retained in `d77/rct4-154-model` (revision `sha256:94417b61aac523e49f9d272935f0d4b11af16ba82fd770d143b5dc4315c6d6ac`), the model uses 1,444 off-diagonal orbit variables, 38 diagonal-pair variables, exact cardinality conditions, and 388,148 deduplicated weighted line constraints. Within its stated subclass, it supplies a sound-and-complete representation and reusable CP-SAT/CNF search infrastructure. A feasible assignment would certify \(D(77)=154\), while infeasibility would exclude only this subclass.

That capability is meaningful even without a solved instance. It changes the research state from an informal symmetry suggestion into an auditable exact search target. The transaction also supplied exact certificate verification and model checking at five calibration sizes, retained in `rct4/calibration-certificates` (revision `sha256:019cf9696cc2e968cac5391e504f5c2bf7d843ecac6c3b777f5c34f6acde1357`). Those checks provide useful regression evidence for the implementation. They do not establish \(n=77\) satisfiability, historical discovery priority, or a general claim about every odd-size record.

Originality credit must be divided by role. The locked state attributes the underlying `rct4` class and symmetry-reduction method to prior work. This transaction should therefore receive credit for independent implementation, specialization to \(n=77\), validation, export and verification tooling, and exact scope management—not for originating the class or the reproduced calibration configurations.

The bounded solver runs merit only computational-reporting credit. The timeouts returned neither a witness nor an infeasibility result, and the locked state assigns them no negative mathematical force. The contribution itself usefully demonstrated this limitation by reporting failures on known satisfiable calibration instances under comparable resource budgets. That honesty improves the quality of the evidence, but the time spent searching should not be mistaken for progress on either endpoint of the certified interval.

The transaction also established the half-turn and quarter-turn orbit obstructions and the grid-center conclusion conditional on half-turn invariance. These became part of `rotational-symmetry/cardinality-obstructions` and `d77/154-half-turn-center`. However, its broader assertion that these exhaust all arbitrary-center rotational possibilities was incompletely justified at this stage. The locked state records the missing arbitrary-center finite-rotation step in `d77/rotational-classification-scope`; the gap was only closed by transaction `29ccbd396781fd36d436ed2e6d0952a4730361b9`. Credit to this transaction should therefore distinguish:

- **full credit** for the half-turn and quarter-turn orbit arguments;
- **full credit** for the center calculation once half-turn invariance is assumed;
- **substantial credit** for identifying and organizing the rotational program;
- **no proof-completion credit** for the arbitrary-center classification later supplied by the fourth transaction.

This qualification does not make the earlier work valueless. It created the `program/rotational-symmetry` program, supplied the strict-subclass model, and exposed a precise proof gap that could be repaired. It thus causally enabled the later correction even though it did not itself complete that theorem.

No research-direction registration predates this transaction. In particular, register event `initial-plan` in transaction `a9552d14dcd11d394a0ae9672b6d81dae033f127` concerns the later repair and cannot retroactively confer direction priority on this contribution. Conversely, that later registration does not diminish the earlier transaction’s priority for the model, calibration infrastructure, and accepted orbit arguments.

**Qualitative significance:** high as enabling infrastructure and as a precisely scoped symmetry-restricted program, but limited as direct progress on \(D(77)\). It produced neither a 154-point certificate nor an impossibility proof, and its model covers a strict subclass of centered half-turn configurations.

## Contribution: 29ccbd396781fd36d436ed2e6d0952a4730361b9

**Primary roles:** proof completion, correction of an omitted step, arbitrary-center classification, and precise exposition.

This transaction supplied the decisive missing argument in the rotational-classification program. Its durable result is the theorem that a nonidentity Euclidean rotation preserving a finite noncollinear subset of \(\mathbb Z^2\), with arbitrary center, must be a half-turn or quarter-turn. It did so by showing that two independent lattice difference vectors and their images force the rotation matrix to be rational, deriving finite order from the induced permutation of the finite set, and then combining rational trace with algebraic integrality and rationality of the sine entry.

That proof closed the qualification previously attached to `d77/rotational-classification-scope`. Its causal effect is visible in the revision-two forms of:

- `program/rotational-symmetry` (revision `sha256:352ab3783d55069d1e5421220a10ec0d37022b40baebc1a04ab6dcd7d9b5e876`);
- `rotational-symmetry/cardinality-obstructions` (revision `sha256:e7a2739fbe660d68fe547d59cec8119a513d0fdd66e0380557d4a40283ab2c6a`);
- `d77/154-half-turn-center` (revision `sha256:e82c0acf3d20d8357ac8dcdb7c25d91f85f68818ee3cc0736993ccf55f29fbf4`);
- `d77/rotational-classification-scope` (revision `sha256:4f974c073a129f68b783f09ef8661a2c6b5e4e8a1ed7edc97e4dd53c16e5cf05`).

The transaction deserves proof credit for the arbitrary-center reduction and for making the resulting 153/154 consequences complete within the rotational scope. It should not receive fresh credit for the half-turn and quarter-turn orbit arguments or the row-and-column occupancy observation, which were already present in earlier canonical work. Its value is that those prior ingredients could not support a complete arbitrary-center conclusion until this omitted theorem was supplied.

The work is self-contained and does not depend on a bounded computation or external factual claim. It also maintains disciplined scope: rotations only, finite noncollinear lattice sets only, no reflection classification, no identification of all centered half-turn sets with `rct4`, and no improvement to \(152\le D(77)\le154\). That precision strengthens the quality of the contribution because it repairs exactly the recorded gap without inflating the consequence.

There is specific preregistration evidence. Register event `initial-plan`, transaction `a9552d14dcd11d394a0ae9672b6d81dae033f127`, named the arbitrary-center theorem, outlined the rational-basis, finite-order, trace, and rational-sine method, identified the exact knowledge nodes to be repaired, and stated the intended scope limitations. It predates this contribution and is closely connected to the eventual proof, so it is meaningful non-exclusive evidence of timely intent and competent direction pursuit.

Follow-through is unusually direct. Completion event `proof-merged`, transaction `bbf27430c8b61446236371c57c58e3b8d6278921`, explicitly links the completed registered direction to this contribution. The merged proof follows the registered method and satisfies the stated completion criterion. Because the registration and completion occurred in a short, tightly coupled workflow, they are strongest as evidence of disciplined execution and ledger-local direction priority, not as evidence of broad historical priority or ownership of the finite-rotation theorem. The locked state expressly leaves broader historical priority unadjudicated.

The transaction’s significance is structural rather than extremal. It fully classifies possible nontrivial rotational symmetry for hypothetical 153- and 154-point configurations, but it neither constructs such a configuration nor excludes asymmetric or reflection-symmetric possibilities. It closes a real proof gap and strengthens the rotational research program without changing the global certified interval.

**Qualitative significance:** a clean and complete correction with strong registered follow-through. It receives primary credit for the arbitrary-center proof step and the resulting complete rotational classification, while sharing the final corollaries with the earlier orbit, center, and occupancy contributions on which they depend.
