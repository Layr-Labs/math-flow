# Knowledge-Formation Report

The current state contains one durable research program devoted to exact certification of explicit determinant witnesses. The central value question and the best supplied global bounds remain at the root because they span all possible approaches to the order-\(23\) maximal-determinant problem.

No conflict records or reconciliation outcomes were supplied. The unresolved exact-value question is therefore represented as an open research question, not as an active dispute between opposed judgments.

## Node: root

**Title:** Research state for maximal-determinant-23  
**Type:** Root  
**Status:** Active

For

\[
D_{23}=\max\left\{|\det A|:A\in\{-1,+1\}^{23\times23}\right\},
\]

the current supplied knowledge state retains the certified bounds

\[
2^{22}\,3\,5^6\,67\,211
=
2{,}779{,}447{,}296{,}000{,}000
\le D_{23}
\le
2^{22}\,3\,5^6\,675\sqrt{505}.
\]

Because \(D_{23}\) is an integer, the supplied problem statement permits replacing the real-valued upper endpoint by its floor. No stronger divisibility rounding or smaller upper endpoint has been established by the assessed evidence.

The immutable primary judgment

`sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`

supports the lower endpoint through an explicit admissible \(23\times23\) sign matrix whose absolute determinant is exactly

\[
2{,}779{,}447{,}296{,}000{,}000.
\]

That judgment expressly finds that the assessed artifact reproduces the already published lower endpoint rather than improving it.

The exact value of \(D_{23}\) remains unresolved in the supplied knowledge state. In particular, the primary judgment does not support

\[
D_{23}=2{,}779{,}447{,}296{,}000{,}000,
\]

because the assessed artifact verifies only one matrix and provides no exhaustive classification, exhaustive search certificate, Gram-matrix impossibility argument, or other proof excluding larger determinants. It likewise supplies neither a witness strictly above the current lower endpoint nor an argument lowering the stated upper endpoint.

The root has one established program:

- `exact-witness-certification` — exact, independently replayable certification of explicit sign-matrix witnesses and their determinants.

The global bound interval and the unresolved exact-value question remain at this root rather than being assigned to that program, since they are relevant to every prospective analytic, arithmetic, computational, classification, or search approach.

**Provenance**

- Frontier source supplied with the problem: William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith, *New lower bounds for the maximal determinant problem* (2003), arXiv:`math/0304410`.
- Immutable primary judgment: `sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.
- Assessed subject and evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- No conflict records or reconciliation judgments were supplied.

## Change: root

The root previously contained only an empty research state. It is expanded because the primary judgment certifies the supplied lower endpoint, preserves the exact-value and upper-bound questions as unresolved, and supports establishing a durable exact-witness-certification program. Global bounds remain at root to avoid assigning cross-program frontier facts to a method-specific program.

## Node: exact-witness-certification

**Title:** Exact certification of explicit maximal-determinant witnesses  
**Type:** Program  
**Parent:** `root`  
**Status:** Active

This program organizes exact and independently replayable certification of explicit sign matrices offered as witnesses for lower bounds on \(D_{23}\). Its scope includes:

- checking that a supplied matrix has exactly \(23\) rows and \(23\) columns;
- checking that all entries belong to \(\{-1,+1\}\);
- evaluating the determinant using exact rather than floating-point arithmetic;
- retaining sufficient artifacts for independent replay; and
- distinguishing certification of a particular witness from proof that the witness is globally optimal.

The program currently contains two durable concepts:

1. `exact-witness-certification/order-23-record-witness`, representing the explicit order-\(23\) sign matrix certified at the published lower endpoint; and
2. `exact-witness-certification/bareiss-replay-method`, representing the fraction-free exact verification method supplied for that matrix.

According to primary judgment

`sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`,

the current artifact is valid, exact, and independently replayable. Its mathematical role is reproducibility and certification of the published witness. It does not improve either numerical frontier and does not establish optimality.

The judgment carries forward the artifact’s allocation of credit: the matrix and determinant record are attributed to William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith, while Robert Raynor is credited with transcription, documentation, and construction of the compact exact verifier. The judgment does not independently reassess discovery or priority.

**Provenance**

- Immutable primary judgment: `sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.
- Subject and evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- The complete matrix and verifier are reported by the judgment as included in that transaction.

## Change: exact-witness-certification

This program is created because the judgment identifies a durable, independently meaningful agenda: exact replay and certification of explicit determinant witnesses. It separates witness verification from the global optimality and bound questions retained at root.

## Node: exact-witness-certification/order-23-record-witness

**Title:** Certified order-\(23\) record witness  
**Type:** Result  
**Parent:** `exact-witness-certification`  
**Status:** Supported with high confidence

The explicit matrix preserved in transaction

`fb88b7832c0fa7e84c1583110a7df800571bca02`

is assessed by primary judgment

`sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`

as a \(23\times23\) matrix \(A\) with entries in \(\{-1,+1\}\) and

\[
|\det A|
=
2^{22}\,3\,5^6\,67\,211
=
2{,}779{,}447{,}296{,}000{,}000.
\]

The judgment supports this claim with high confidence because the transaction supplies both the complete sign matrix and a deterministic exact verifier. The verifier enforces the dimensions and admissible entries and compares the determinant computed from the parsed matrix with the stated factor product.

As an admissible matrix with that determinant, the witness certifies

\[
D_{23}\ge 2{,}779{,}447{,}296{,}000{,}000.
\]

This is the published lower endpoint already present in the problem statement. The witness therefore certifies the known record but does not establish a strictly larger lower bound.

The witness does not establish that its determinant equals \(D_{23}\). The primary judgment records that the artifact contains no exhaustive enumeration, Gram-matrix classification, replayable nonexistence certificate, or other optimality proof excluding matrices with larger determinants. No upper-bound improvement follows from this witness.

**Evidentiary qualification**

The transaction does not include a generated execution transcript or a list of intermediate Bareiss pivots. Consequently, the large determinant arithmetic is not displayed step by step in the preserved report. The primary judgment does not treat this as a material defect because the complete matrix and deterministic exact verifier are supplied and can be independently executed.

**Attribution and source qualification**

The judgment carries forward the README attribution of the matrix and determinant record to William P. Orrick, Bruce Solomon, Roland Dowdeswell, and Warren D. Smith.

The included hashes can assist in checking an externally retrieved arXiv archive and `matData.tex`, but those external source files are not themselves included in the assessed transaction. The judgment therefore does not regard row-for-row transcription from that particular external source version as independently established solely by the included files. This provenance qualification does not weaken the determinant certification, which depends on the matrix and exact verifier actually included in the transaction.

**Provenance**

- Immutable primary judgment: `sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.
- Subject and evidence transaction: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.
- Frontier attribution carried by the judgment: Orrick, Solomon, Dowdeswell, and Smith.

## Change: exact-witness-certification/order-23-record-witness

This result node is created because the judgment supports a distinct durable mathematical fact: an explicit admissible order-\(23\) sign matrix has the published record determinant. The node preserves the judgment’s confidence, replay qualification, non-optimality limitation, and attribution without treating the transaction itself as a knowledge node.

## Node: exact-witness-certification/bareiss-replay-method

**Title:** Fraction-free exact determinant replay for the order-\(23\) witness  
**Type:** Method  
**Parent:** `exact-witness-certification`  
**Status:** Supported with high confidence

The verifier assessed in transaction

`fb88b7832c0fa7e84c1583110a7df800571bca02`

provides an exact, deterministic replay method for the determinant of the explicit order-\(23\) witness. Primary judgment

`sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`

characterizes the implementation as a standard fraction-free Bareiss elimination using Python integers rather than floating-point arithmetic.

As recorded by the judgment, the verifier:

1. requires exactly \(23\) matrix rows;
2. requires exactly \(23\) sign characters in every row;
3. rejects characters other than `+` and `-`;
4. converts those characters to \(+1\) and \(-1\);
5. copies the input before determinant elimination;
6. searches for a nonzero pivot in the active column;
7. tracks the determinant sign resulting from row interchanges;
8. performs elimination using exact integer operations;
9. uses `divmod` and aborts if a required Bareiss division is not exact;
10. returns the final Bareiss entry with the accumulated row-swap sign correction; and
11. compares the absolute determinant computed from the matrix against the expected factor product.

The judgment finds that row pivoting among active rows is handled consistently through the recorded row-swap sign and that failure to find a required pivot would result in a zero determinant, which would fail the expected nonzero comparison.

The verifier is independently replayable using the supplied matrix and the Python standard library. Its supported scope is exact certification of the determinant of the supplied witness. It is not an exhaustive search, a Gram-matrix classification, an upper-bound argument, or a proof that the witness is optimal.

No execution transcript or intermediate pivot list is included. The primary judgment treats this as a non-material evidentiary qualification because the complete deterministic verifier is available for direct audit and execution.

**Credit**

The judgment carries forward credit to Robert Raynor for transcription, documentation, and construction of the compact exact verifier. It does not attribute discovery of the matrix or determinant record to him.

**Provenance**

- Immutable primary judgment: `sha256:34be73e7adced95684a58544e50a7ce03a8781b860fa3ba1640129f3bdfb687d`.
- Subject and evidence transaction containing the matrix and verifier: `fb88b7832c0fa7e84c1583110a7df800571bca02`, ledger position 1.

## Change: exact-witness-certification/bareiss-replay-method

This method node is created because the exact fraction-free replay procedure is a durable verification concept distinct from the certified matrix itself. Its scope and limitations are taken directly from the primary judgment, including the absence of an execution transcript and the lack of any optimality or frontier-improvement claim.
