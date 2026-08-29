# BSSC research-v6 serial producer

Status: runtime and hosted-route candidate for a separately admitted
`openrouter-research-v6` projection. Admission remains a one-file governed PR.

V6 is a fresh-from-zero Builder V8 experiment over the same 16 canonical
accepted BSSC submissions used by V5. It preserves the two-entity state-v3
model—hierarchical programs plus bundled intermediate results—but changes the
context and trusted output boundary in three places.

## Builder V8 changes

### Complete validity assessment

Builder V7 received only `claimKey`, the contributor's declared `statement`,
and accepted dependency transaction IDs. That discarded three fields already
present in validity-v4: `validitySummary`, `scopeQualifications`, and
`evidenceTransactionIds`. A qualified accepted claim could therefore be
reintroduced as the contributor's broader raw assertion.

Builder V8 seals `research-builder-submission-input-v2`. Each accepted claim
contains:

- `declaredStatement`, explicitly labeled as the contributor's raw assertion;
- the authoritative `validitySummary`;
- the exact sorted `scopeQualifications`;
- `evidenceTransactionIds`; and
- `dependencyTransactionIds`.

The prompt and retry contract state that the declared assertion cannot override
the adjudication. The stored input is content-addressed and replay validation
checks the richer envelope.

### Exact evidence binding

The model selects repository `artifactPaths` from the exact current submission
evidence. It never authors artifact digests. Trusted code replaces selected
paths with exact `{path, digest}` references from the verified evidence
manifest, preserves prior references when consolidating into an existing
result, and rejects an unknown path.

Every intermediate result mapped to the current contribution must include at
least one exact current-submission artifact. Any new artifact reference in an
operated result must belong to the current evidence manifest. These properties
are rechecked while loading the published bundle; they are not only prompt
instructions.

### Affected-ancestor synthesis

For every direct program, linked result program, and changed topology scope,
trusted validation computes the affected program closure in both the before
and after states. Every affected program that existed in the predecessor—and
every existing ancestor through root—must have an operation in the transition
and must add the current subject to `sourceTransactionIds`.

This is a semantic freshness boundary, not deterministic prose generation.
Trusted code can prove that every relevant summary was re-authored against the
new portfolio, while the builder remains responsible for the mathematical
synthesis. It directly prevents the V5 K2 behavior where a new child program
and result were created but root retained its K1-only summary.

## Preserved contracts

V8 deliberately reuses research state schema V3, topology alignment V2, and
same-world handoff V2. The state still contains only programs and intermediate
results, accounting nodes remain programs only, one build handles exactly one
accepted submission, and the V7 reducer continues to enforce stable identity,
reciprocal links, additive provenance, acyclic result dependencies, placement,
and atomic topology changes. V7, V5, and all published V5 bytes remain
unchanged and replayable.

The new governed identities are:

- builder implementation `openrouter-hierarchical-research-builder-v8`;
- output profile `math-flow/hierarchical-research-v8`;
- sealed accepted-submission input V2;
- stored transition schema V8; and
- candidate projection `openrouter-research-v6`.

## Fresh BSSC frontier and hosted route

`bssc-research-v6-frontier` reuses the immutable pinned validity-v4 source and
accepts the same canonical ledger ordinals:

```text
3, 4, 5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 24, 25
```

It starts from the state-v3 zero state and never uses a V5 state as a
predecessor. Each predecessor must be a V8 bundle in the exact governed V6
chain. `.github/workflows/project-research-v6-serial.yml` is the only intended
hosted route. It defaults `continue` to false, claims one subject, makes one
provider formation call with bounded governed retries, atomically publishes the
bundle and scheduler, and continues only when explicitly requested. The generic
OpenRouter workflow rejects V6 before provider access.

## Credit-assignment boundary

This change does not create or silently retarget a credit projection. Existing
work-accounting V1 and V2 remain bound to `openrouter-research-v4`; historical
research-credit V3 remains bound to `openrouter-research-v3`.

The provider-neutral state-v3 accounting reducer, program-only node model,
impact-context V2, and same-world handoff support already exist. A V8-based
credit experiment still needs an additive published-transition adapter, new
governed work-accounting identities, a projection dependency on
`openrouter-research-v6`, and its own hosted lane. Keeping that activation
separate prevents a credit experiment from being coupled to an uninspected
knowledge-builder run.
