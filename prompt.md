I want to create an app for collaborative problem solving on math challenges. 



It would have two layers: 

- Canonical transaction layer
- Pluralistic state layer



The canonical transaction layer takes in contributions from participants. There may or may not be objective validation operations such as lean verification taken at this stage. The transactions are stored as a canonical ledger.



The pluralistic state layer uses AI judges to wrap up the transactions into a current problem state.  There are a few types of operations that judges will perform: 

- Acceptance / rejection of a given contribution as correct
- Formation of a cumulative view of the knowledge state
- Assignment of credit. 



Since a given AI judge may not be entirely trustworthy, we want a way to be able to overlay multiple AI judges on the same transaction record, perhaps retroactively. 



I want to explore possible architectures for getting something like this running quickly. Possible tools used by the org are github, github apps, and vercel. 


********

Yes. The cleanest architecture is to treat this as an **event-sourced protocol with plural, replayable projections**.

The central design principle I’d use is:

> **Canonicalize what participants did, not what it means.**

Correctness, synthesis, and credit are interpretations of the canonical history. Even “objective” verification like Lean is best represented as an attestation attached to a transaction rather than silently mutating the transaction itself.

## 1. Core data model

I would make the canonical layer extremely small.

```text
Problem
  |
  +-- Transaction 1
  +-- Transaction 2
  +-- Transaction 3
  +-- Transaction 4
           |
           +---- objective attestations
           |       Lean: valid
           |       syntax-check: valid
           |
           +---- judge A interpretation
           +---- judge B interpretation
           +---- judge C interpretation
```

A transaction might look roughly like:

```ts
type Transaction = {
  id: string
  problemId: string

  // monotonically increasing within problem
  seq: number

  author: {
    githubUserId?: string
    displayName?: string
  }

  type:
    | "claim"
    | "proof"
    | "counterexample"
    | "correction"
    | "comment"
    | "formalization"

  content: string

  // optional explicit relationships
  references: string[]   // transaction IDs

  createdAt: string
}
```

I'd avoid putting fields such as `accepted`, `score`, or `credit` here.

Then add immutable **attestations**:

```ts
type Attestation = {
  transactionId: string

  verifier: "lean-4.XX" | "judge-X" | "human-reviewer"
  verifierVersion: string

  result: object

  createdAt: string
}
```

Lean saying a proof checks is a fact about a particular submission under a particular verifier environment. It doesn't necessarily mean the contribution is relevant, novel, or answers the intended mathematical question.

---

# 2. Make judge state explicitly addressable

The most important identifier in the pluralistic layer is something like:

```text
(problem_id, ledger_cursor, judge_spec)
```

For example:

```text
problem: P173
transactions: 1..428

judge_spec:
    model: gpt-X
    judge-code: abc123
    prompt: sha256:91e...
    rubric: v7
```

And its output:

```ts
type JudgeProjection = {
  problemId: string
  throughSeq: number
  judgeSpecId: string

  contributionVerdicts: {
    transactionId: string
    status: "accepted" | "rejected" | "uncertain"
    confidence: number
    rationale: string
  }[]

  knowledgeState: KnowledgeState

  creditAssignments: CreditAssignment[]
}
```

This means you never have to answer:

> "What is the state of problem X?"

without implicitly answering:

> "According to whom?"

You can have:

```text
                 Ledger through tx 428
                         |
         +---------------+---------------+
         |               |               |
      Judge A          Judge B          Judge C
         |               |               |
      State A          State B          State C
```

And six months later:

```text
Judge D v1
   replay transactions 1..428
        ↓
new State D
```

No migration of the canonical data is needed.

---

# 3. I see three plausible MVP architectures

### A. GitHub-native

Use GitHub itself almost as the protocol.

```text
Contributors
     ↓
GitHub Issues / PRs / comments
     ↓
GitHub App
     ↓
normalized transaction JSON
     ↓
Git repository
     ↓
GitHub Actions
 ├── Lean verifier
 ├── Judge A
 └── Judge B
```

You could store something like:

```text
/problems/IMO-2026-1/problem.md

/problems/IMO-2026-1/transactions/
  000001.json
  000002.json
  000003.json

/problems/IMO-2026-1/projections/
  judge-a/
    000003.json
  judge-b/
    000003.json
```

A GitHub App can receive repository webhooks and take actions in response, which makes ingestion from issues/PRs quite straightforward. ([GitHub Docs][1]) GitHub Actions can run jobs on hosted or self-hosted runners, including workflows triggered by repository activity, manually, on schedules, or via the API. ([GitHub Docs][2])

**Advantages:** extremely easy to inspect/debug, history is naturally versioned, your protocol artifacts are human-readable, external researchers can clone the entire history, and GitHub Actions is a convenient place to run Lean.

**Disadvantages:** Git becomes an awkward database surprisingly quickly. Concurrent appends, querying thousands of transactions, permissions, user experience, and frequently updating projections are all somewhat unnatural. Git history is also not inherently an immutable ledger—you'd still need branch protections/conventions if tamper resistance matters.

I like this architecture for a **research prototype**, especially if the first users are already GitHub-native.

---

********

I like the github starting point. I just have a few questions: 



- What happens to the Github PR after the Github app has normalized it? Is the original PR closed and a new one created? 
- I don't think we should force submissions to fit in a schematic json file. Plain text seems to be a better format. Transactions should generally be an entire folder that contains a markdown file and potentially other artifacts such as executable code. 
- Does the github app allow us to construct a canonical sequencing of transactions? 


*********

I’d revise the GitHub-first design in exactly that direction. The key move is: **a transaction is a Git tree/commit, not a JSON record**.

### 1. What happens to the original PR?

I would **not create a replacement PR**.

The lifecycle should be:

```text
Contributor opens PR
        │
        ▼
GitHub App inspects it
        │
        ├── structural checks
        ├── optional Lean / executable checks
        └── maybe AI pre-review
        │
        ▼
App posts GitHub Check
        │
        ▼
PR accepted
        │
        ▼
Squash-merge into canonical branch
        │
        ▼
Resulting commit = canonical transaction
```

GitHub Apps are particularly well suited to acting as checks: GitHub's Checks API lets an App create check runs against commits, so the App doesn't have to rewrite the contribution at all. ([GitHub Docs][1])

After it is accepted, the original PR simply becomes a **merged PR**. It remains around permanently as the discussion/review context surrounding the canonical transaction. GitHub's normal model is exactly that: a PR proposes changes to a base branch, and merging incorporates those changes into the branch. ([GitHub Docs][2])

So I would actually weaken the word **"normalize."** The App mostly *validates and annotates*. It need not transform the submission.

You end up with a useful distinction:

```text
PR #137
    = social object
      discussion
      reviews
      iteration
      failed checks
      author identity
      timestamps

          ↓ accepted

commit abc123...
    = protocol object
      canonical transaction
```

That seems very clean.

---

### 2. Yes: make the transaction an arbitrary directory tree

I strongly prefer your proposal.

For example:

```text
problems/
  pythagorean-variants/
    problem.md

    contributions/
      some-contribution-id/
        README.md
        proof.lean
        helper.py
        diagram.svg
        notes/
          derivation.md
```

The only convention I'd initially impose is something like:

```text
Every transaction adds exactly one directory.

That directory must contain:
    README.md

Everything else is arbitrary.
```

`README.md` is the human-readable contribution:

```markdown
## Claim

It is enough to prove that ...

## Argument

Consider the following construction...

## Notes

`proof.lean` contains a formalization of Lemma 2.
```

And the rest is just files.

This maps beautifully onto Git itself because a Git commit is a snapshot containing a tree of files/directories; GitHub exposes those tree and commit objects directly through its API as well. ([GitHub Docs][3])

I wouldn't even require a `transaction.json` initially.

A lot of metadata already exists outside the folder:

```text
transaction ID       → canonical Git commit SHA
content              → Git tree
author/proposer      → source PR
discussion           → source PR
submission time      → source PR
canonicalization time→ merge time
parent transaction   → parent Git commit
```

You might eventually want a tiny amount of machine-readable metadata, but I'd resist adding it until you have a concrete need.

For instance, explicit references could easily remain Markdown:

```markdown
This extends the argument from #118.

The construction in #94 appears to fail because...
```

The AI layer can understand that just fine, while more formal cross-transaction references can be introduced later.

---

### 3. Git can itself provide the canonical sequencing

This is the part that makes the design especially attractive.

Imagine the canonical branch is:

```text
main

A ← B ← C ← D ← E
```

Each commit has exactly one parent.

If:

```text
A = initial problem
B = transaction 1
C = transaction 2
D = transaction 3
E = transaction 4
```

then **the Git history is already your canonical ledger**.

You don't need the GitHub App to manufacture sequence numbers.

You can define:

```text
Transaction order :=
    commit order on canonical branch
```

and identify any ledger prefix by its head commit:

```text
state according to judge J
at commit D
```

rather than:

```text
state according to judge J
after transaction_number = 3
```

That is considerably nicer protocol-wise because the parent pointers give you a hash-linked history.

---

### Enforcing one PR → one transaction

For the canonical branch I'd configure GitHub fairly aggressively:

```text
canonical/main

✓ Changes only through PRs
✓ Required "valid transaction" GitHub App check
✓ Only squash merging
✓ Linear history
✓ Force pushes disabled
✓ Branch deletion disabled
```

GitHub supports requiring status checks and linear history through branch protection/rulesets. A linear-history rule prevents merge commits; if the repo allows only **Squash and Merge**, each accepted PR becomes a single commit on the canonical branch. ([GitHub Docs][4])

So:

```text
PR #51
  contributor makes 7 WIP commits
             ↓
          squash
             ↓
canonical commit 8fac...

PR #52
  contributor makes 3 WIP commits
             ↓
          squash
             ↓
canonical commit 290b...
```

Canonical ledger:

```text
... → 8fac → 290b
       #51    #52
```

The contributor gets to use Git normally while working, but the protocol sees exactly **one atomic transaction per accepted PR**.

That feels like the right semantic boundary.

---

### Does the App decide sequence?

I'd actually say **no, intentionally**.

The App determines:

```text
Is this transaction admissible for inclusion?
```

GitHub determines:

```text
Which accepted transaction lands next?
```

And Git determines:

```text
What is the canonical history?
```

For an early system, normal PR merging is probably sufficient. There is intrinsically a single resulting ordering on the canonical branch.

If concurrency gets high enough that two or twenty accepted contributions are waiting simultaneously, GitHub has a **merge queue** specifically for this. GitHub documents its queue as merging PRs in first-in-first-out order while making sure required checks remain satisfied against the relevant accumulated state. ([GitHub Docs][5])

So the eventual flow can become:

```text
             PR #101 ── check ✓ ─┐
             PR #102 ── check ✓ ─┤
             PR #103 ── check ✓ ─┤
                                  ▼
                            GitHub merge queue
                                  │
                          canonical ordering
                                  │
                                  ▼
                     T501 → T502 → T503
```

One caveat: GitHub merge queues are currently available for public repositories owned by organizations, and for private organization repositories on Enterprise Cloud. ([GitHub Docs][5]) So I wouldn't make that an MVP dependency.

---

## One tweak I particularly like

I would **not put sequence numbers into transaction directory names**.

Avoid:

```text
transactions/
  000001/
  000002/
  000003/
```

because now whoever submits a PR needs to know which number they will receive, which creates unnecessary concurrency problems.

Instead:

```text
contributions/
  7fbc2a/
  a91e30/
  my-cyclic-construction/
```

or some generated immutable ID.

Then sequence comes entirely from Git:

```text
commit 7df...   contribution foo    ordinal 1
commit 821...   contribution bar    ordinal 2
commit 031...   contribution baz    ordinal 3
```

If the UI wants convenient numbers, it can derive `#1`, `#2`, `#3` from history.

That keeps **identity** and **ordering** separate.

---

## And this makes the pluralistic layer even cleaner

A judge doesn't actually need an SQL-style cursor anymore.

Its input can literally be:

```text
repository:
    math-collab/problems

problem:
    IMO-2026-3

ledger_head:
    031ac785...

judge:
    judge-spec-v4
```

Conceptually:

```text
git checkout 031ac785

read:
  problem.md
  contributions/**

              ↓

        AI Judge v4

              ↓

projection rooted at 031ac785
```

And later:

```text
                 canonical Git history

A ─── B ─── C ─── D ─── E
                    │
              ┌─────┼─────┐
              ▼     ▼     ▼
           Judge A  B     C
              │     │     │
             S_A   S_B   S_C
```

That gives you a fairly profound property for very little infrastructure:

**Anyone who can clone the repository has the complete canonical input required to replay a judge.**

The PRs then provide a richer GitHub-native social/audit layer around that ledger, while Git itself contains the durable mathematical artifacts.

[1]: https://docs.github.com/en/rest/checks/runs?utm_source=chatgpt.com "REST API endpoints for check runs - GitHub Docs"
[2]: https://docs.github.com/articles/about-pull-requests?%2F=&utm_source=chatgpt.com "Pull requests - GitHub Docs"
[3]: https://docs.github.com/en/rest/git/trees?utm_source=chatgpt.com "REST API endpoints for Git trees - GitHub Docs"
[4]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches?ref=grant-winney&utm_source=chatgpt.com "About protected branches - GitHub Docs"
[5]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue?apiVersion=2022-11-28&utm_source=chatgpt.com "Managing a merge queue - GitHub Docs"
